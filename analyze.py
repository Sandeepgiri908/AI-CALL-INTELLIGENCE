import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)


def analyze_call(transcript):

    prompt = f"""
You are an AI Call Intelligence platform.

Analyze the following customer conversation.

Transcript:
{transcript}

Return in this format:

Summary:
Intent:
Sentiment:
Objection:
Lead Score:
Retargeting Segment:
Next Best Action:

Retargeting Segment must be one of:
- Strike Now
- Nurture
- Handle Objection
- Re-engage
- Do Not Contact

Lead Score:
0-30 = Low Interest
31-70 = Moderate Interest
71-100 = High Interest

Keep answers concise and business-friendly.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    sample_transcript = """
    My name is Sandi. I am interested in home loan. Can you provide me home loan?
    """

    result = analyze_call(sample_transcript)

    print("\nAI ANALYSIS:\n")
    print(result)