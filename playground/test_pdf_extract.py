import pymupdf
import os

def create_dummy_pdf(filename="playground/sample_resume.pdf"):
  """Create a sample PDF if you don't have one ready."""
  doc = pymupdf.open()
  page = doc.new_page()
  sample_text = """
  CHAN SREYMOM
  Phnom Penh, Cambodia | sreymom.chan@gmail.com
  
  EDUCATION
  Cambodia Academy of Digital Technology (CADT)
  Bachelor of Computer Science (Telecommunication & Networking)
  GPA: 3.80
  
  ACADEMIC COURSES
  - Cloud Computing & Distributed Systems
  - Network Security & Cryptography
  - Object Oriented Programming with Java
  
  TECHNICAL SKILLS
  Languages: Python, Java, Bash
  Infrastructure & Tools: Docker, Linux, AWS, Git, Wireshark
  """
  page.insert_text((50, 50), sample_text, fontsize=11)
  doc.save(filename)
  doc.close()
  print(f"📄 Created sample PDF at: {filename}")

def extract_text_from_pdf(pdf_path: str) -> str:
  """Extracts all text from a PDF file using PyMuPDF."""
  if not os.path.exists(pdf_path):
      print(f"⚠️ File not found at {pdf_path}. Generating a dummy one...")
      create_dummy_pdf(pdf_path)

  text = ""
  with pymupdf.open(pdf_path) as doc:
      for page_num in range(len(doc)):
          page = doc[page_num]
          text += page.get_text() + "\n"
          
  return text.strip()

# Run the test
if __name__ == "__main__":
  test_pdf = "playground/sample_resume.pdf"
  
  print(f"🔍 Extracting raw text from: {test_pdf}")
  extracted_text = extract_text_from_pdf(test_pdf)
  
  print("\n--- Extracted Raw Text ---")
  print(extracted_text)
  print("\n✅ PyMuPDF successfully read the PDF!")