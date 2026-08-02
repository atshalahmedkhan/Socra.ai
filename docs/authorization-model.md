# Authorization model

Roles never come from request bodies. Membership is loaded for the exact classroom resource.

| Permission | Student | TA | Instructor |
|---|:---:|:---:|:---:|
| classroom:read | ✓ | ✓ | ✓ |
| member:read |  | ✓ | ✓ |
| member:manage |  |  | ✓ |
| material:read | ✓ | ✓ | ✓ |
| material:create |  | ✓ | ✓ |
| material:delete |  |  | ✓ |
| session:create/read own/message:create/feedback:create | ✓ |  |  |
| session:read classroom aggregate |  | ✓ | ✓ |

Research permission is a separate `is_researcher` identity attribute and is not implied by instructor membership. Admin is explicit and does not implicitly waive privacy rules. Direct anonymous database access is denied for product identity/classroom tables.
