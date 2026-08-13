from transcribe import transcribe_audio
from analyze import analyze_call
from database import save_call_analysis

audio_path = "uploads/Recording.m4a"

customer_name = "Sandeep"
phone_number = "9999999999"

print("Step 1: Transcribing audio...")
transcript = transcribe_audio(audio_path)

print("\nTRANSCRIPT:\n")
print(transcript)

print("\nStep 2: Analyzing transcript...")
analysis = analyze_call(transcript)

print("\nAI ANALYSIS:\n")
print(analysis)

print("\nStep 3: Saving to MySQL...")
save_call_analysis(customer_name, phone_number, transcript, analysis)