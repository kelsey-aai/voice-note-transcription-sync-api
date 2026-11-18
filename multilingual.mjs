import { AssemblyAI } from "assemblyai";

const apiKey = process.env.ASSEMBLYAI_API_KEY;
if (!apiKey) {
  console.error("Set ASSEMBLYAI_API_KEY");
  process.exit(1);
}

const client = new AssemblyAI({ apiKey });

// You know this user's threads are in Spanish and English.
const result = await client.sync.transcribe("./voice_note.wav", {
  model: "universal-3-6-pro",
  language_codes: ["es", "en"],
});

console.log(result.text);
