import { AssemblyAI } from "assemblyai";

const apiKey = process.env.ASSEMBLYAI_API_KEY;
if (!apiKey) {
  console.error("Set ASSEMBLYAI_API_KEY");
  process.exit(1);
}

const client = new AssemblyAI({ apiKey });

await client.sync.warm(); // open the connection as soon as you know a note is coming
const result = await client.sync.transcribe("./voice_note.wav", {
  model: "universal-3-6-pro",
});

console.log(result.text);
