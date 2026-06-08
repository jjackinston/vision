import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const VOICE_SYSTEM = `You are SellerVision AI's Voice Business Assistant — the AI CEO of an e-commerce business.
Answer questions about business performance, inventory, products, and recommendations.
Keep responses under 2 sentences — they will be spoken aloud.
Be direct, specific, and actionable. Use real-sounding metrics.
Examples:
- "Your top product this week is the Bamboo Cutting Board with $3,200 revenue."
- "You have 2 products at critical stockout risk — Widget Pro needs reorder within 11 days."
- "Your best opportunity right now is expanding Product B to Walmart — projected $2,100/month additional profit."`;

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();
    if (!query?.trim()) {
      return NextResponse.json({ error: "Query required" }, { status: 400 });
    }

    const message = await client.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 150,
      system: VOICE_SYSTEM,
      messages: [{ role: "user", content: query }],
    });

    const response = (message.content[0] as any).text;
    return NextResponse.json({ response, query });
  } catch (error: any) {
    console.error("Voice assistant error:", error);
    return NextResponse.json(
      { response: "I'm having trouble accessing your data right now. Please try again.", error: error.message },
      { status: 200 }
    );
  }
}
