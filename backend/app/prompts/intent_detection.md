# Intent Detection Prompt

Classify the user's message into EXACTLY ONE of the following intent categories.

## Categories

- `symptom_analysis` - The user describes symptoms, pain, discomfort, feeling unwell, and wants to understand possible causes.
- `medicine` - The user asks about a medicine, drug, tablet, dosage, side effects, or drug interactions.
- `doctor` - The user asks for a doctor, specialist, consultation, or what kind of doctor to see.
- `emergency` - The user reports signs of an emergency: chest pain, difficulty breathing, stroke signs (face drooping, arm weakness, slurred speech), severe bleeding, loss of consciousness.
- `appointment` - The user wants to book, reschedule, cancel, or view an appointment.
- `general` - Anything else: greetings, general health questions, small talk, navigation, help.

## Emergency priority

If the message could be an emergency, ALWAYS return `emergency` regardless of other content.

## Output format

Respond with a single JSON object, nothing else:

{"intent": "<category>", "confidence": 0.0-1.0}
