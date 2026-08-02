/* Generates config.js from Vercel/local env vars at build time */
const fs = require('fs');

const url = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL || '';
const modernKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
  || process.env.SUPABASE_PUBLISHABLE_KEY || '';
const legacyKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  || process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_KEY || '';

if (modernKey.startsWith('sb_secret_') || legacyKey.startsWith('sb_secret_')) {
  console.error('Invalid frontend Supabase configuration: privileged keys are not browser-safe');
  process.exit(1);
}

if (modernKey && legacyKey && modernKey !== legacyKey) {
  console.error(
    'Conflicting configuration: NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY and NEXT_PUBLIC_SUPABASE_ANON_KEY'
  );
  process.exit(1);
}

const key = modernKey || legacyKey;

if (!url || !key) {
  console.error(
    'Missing Supabase URL or publishable key. Use NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY; legacy anon names remain temporarily supported.'
  );
  process.exit(1);
}

const content = `/* config.js — auto-generated at build; do not commit */
const SUPABASE_URL = ${JSON.stringify(url)};
const SUPABASE_PUBLISHABLE_KEY = ${JSON.stringify(key)};
const sb = supabase.createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
`;

fs.writeFileSync('config.js', content);
console.log('Wrote config.js');
