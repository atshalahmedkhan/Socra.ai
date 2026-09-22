import { NextRequest, NextResponse } from "next/server";
import {
  GUARDRAIL_REWRITE_PROMPT,
  SOCRATIC_SYSTEM,
  violatesSocraticGuardrail,
} from "@/lib/socratic-guardrails";

type Turn = { message: string; isAI: boolean };

async function callGemini(
  apiKey: string,
  topic: string,
  contents: { role: string; parts: { text: string }[] }[],
  extraSystem?: string
) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=${apiKey}`;

  const systemText = extraSystem
    ? `${SOCRATIC_SYSTEM}\n\nCurrent practice topic: ${topic}\n\n${extraSystem}`
    : `${SOCRATIC_SYSTEM}\n\nCurrent practice topic: ${topic}`;

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      systemInstruction: {
        parts: [{ text: systemText }],
      },
      contents,
      generationConfig: {
        temperature: 0.6,
        maxOutputTokens: 350,
      },
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    let friendly = `Gemini error: ${res.status}`;
    if (res.status === 402 || errText.includes("RESOURCE_EXHAUSTED")) {
      friendly =
        "Gemini credits are depleted. Add billing/credits at https://ai.studio/projects then try again.";
    } else if (res.status === 400 || res.status === 403) {
      friendly =
        "Gemini rejected the request. Check that GEMINI_API_KEY in .env.local is valid.";
    }
    throw Object.assign(new Error(friendly), {
      status: 502,
      detail: errText,
    });
  }

  const data = await res.json();
  return (
    data.candidates?.[0]?.content?.parts
      ?.map((p: { text?: string }) => p.text ?? "")
      .join("")
      .trim() || ""
  );
}

const SAFE_FALLBACK =
  "I won't hand you the answer — that defeats the practice. What have you already tried on this, and which step feels unclear?";

export async function POST(req: NextRequest) {
  const apiKey = process.env.GEMINI_API_KEY;

  if (!apiKey) {
    return NextResponse.json(
      {
        error:
          "Missing GEMINI_API_KEY. Put it in frontend/.env.local then restart npm run dev.",
      },
      { status: 500 }
    );
  }

  let body: { topic?: string; messages?: Turn[] };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const topic = body.topic?.trim() || "general CS";
  const history = body.messages ?? [];

  const contents = history.map((m) => ({
    role: m.isAI ? "model" : "user",
    parts: [{ text: m.message }],
  }));

  if (contents.length === 0 || contents[contents.length - 1].role !== "user") {
    return NextResponse.json(
      { error: "Last message must be from the student." },
      { status: 400 }
    );
  }

  try {
    let reply = await callGemini(apiKey, topic, contents);

    // Guardrail pass: if model leaked an answer, force a Socratic rewrite
    if (violatesSocraticGuardrail(reply)) {
      const rewriteContents = [
        ...contents,
        { role: "model", parts: [{ text: reply || "(empty)" }] },
        {
          role: "user",
          parts: [
            {
              text: "Rewrite your last message under Socra's Socratic rules.",
            },
          ],
        },
      ];
      reply = await callGemini(
        apiKey,
        topic,
        rewriteContents,
        GUARDRAIL_REWRITE_PROMPT
      );
    }

    if (!reply || violatesSocraticGuardrail(reply)) {
      reply = SAFE_FALLBACK;
    }

    return NextResponse.json({ reply });
  } catch (err) {
    const e = err as Error & { status?: number; detail?: string };
    if (e.status === 502) {
      return NextResponse.json(
        { error: e.message, detail: e.detail },
        { status: 502 }
      );
    }
    return NextResponse.json(
      { error: e.message || "Request failed" },
      { status: 500 }
    );
  }
}
