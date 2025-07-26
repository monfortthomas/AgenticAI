import os

def log_transcripts(transcripts, path="interview_log.txt"):
    with open(path, "w", encoding="utf-8") as f:
        for i, (question, answer) in enumerate(transcripts):
            f.write(f"Q{i+1}: {question}\nA{i+1}: {answer}\n\n")
    print(f"Transcript saved to {path}")

def log_feedback(feedback_log, path="interview_feedback.txt"):
    with open(path, "w", encoding="utf-8") as f:
        for i, entry in enumerate(feedback_log):
            f.write(f"Q{i+1}: {entry['question']}\n")
            f.write(f"A{i+1}: {entry['answer']}\n")
            f.write(f"Eval: {entry['evaluation']}\n\n")
    print(f"Feedback saved to {path}")

def log_summary(summary, path="interview_summary.txt"):
    # Extract only the final summary starting from "Overall Summary:"
    lines = summary.splitlines()
    final_lines = [line for line in lines]
    final_summary = "\n".join(final_lines)

    with open(path, "w", encoding="utf-8") as f:
        f.write(final_summary)
    print(f"Summary saved to {path}")
