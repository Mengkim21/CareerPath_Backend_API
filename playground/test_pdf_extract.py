import pymupdf
import os

# Version 1
# def create_dummy_pdf(filename="playground/sample_resume.pdf"):
#   """Create a sample PDF if you don't have one ready."""
#   doc = pymupdf.open()
#   page = doc.new_page()
#   sample_text = """
#   CHAN SREYMOM
#   Phnom Penh, Cambodia | sreymom.chan@gmail.com
  
#   EDUCATION
#   Cambodia Academy of Digital Technology (CADT)
#   Bachelor of Computer Science (Telecommunication & Networking)
#   GPA: 3.80
  
#   ACADEMIC COURSES
#   - Cloud Computing & Distributed Systems
#   - Network Security & Cryptography
#   - Object Oriented Programming with Java
  
#   TECHNICAL SKILLS
#   Languages: Python, Java, Bash
#   Infrastructure & Tools: Docker, Linux, AWS, Git, Wireshark
#   """
#   page.insert_text((50, 50), sample_text, fontsize=11)
#   doc.save(filename)
#   doc.close()
#   print(f"📄 Created sample PDF at: {filename}")

# def extract_text_from_pdf(pdf_path: str) -> str:
#   """Extracts all text from a PDF file using PyMuPDF."""
#   if not os.path.exists(pdf_path):
#       print(f"⚠️ File not found at {pdf_path}. Generating a dummy one...")
#       create_dummy_pdf(pdf_path)

#   text = ""
#   with pymupdf.open(pdf_path) as doc:
#       for page_num in range(len(doc)):
#           page = doc[page_num]
#           text += page.get_text() + "\n"
          
#   return text.strip()

# # Run the test
# if __name__ == "__main__":
#   test_pdf = "playground/sample_resume.pdf"
  
#   print(f"🔍 Extracting raw text from: {test_pdf}")
#   extracted_text = extract_text_from_pdf(test_pdf)
  
#   print("\n--- Extracted Raw Text ---")
#   print(extracted_text)
#   print("\n✅ PyMuPDF successfully read the PDF!")

# Version 2
# PDF_FILE_PATH = "playground/dummyResume/resume_test_v1.pdf"

# def extract_text(pdf_path: str) -> str:
#     if not os.path.exists(pdf_path):
#         print(f" Error: Cannot find file at '{pdf_path}'")
#         print("Please copy your resume into the playground/ folder and name it 'my_resume.pdf'")
#         exit(1)

#     full_text = ""
#     with pymupdf.open(pdf_path) as doc:
#         print(f" Found PDF with {len(doc)} page(s).")
#         for page_num in range(len(doc)):
#             page = doc[page_num]
#             text = page.get_text()
#             full_text += f"\n--- PAGE {page_num + 1} ---\n" + text
            
#     return full_text.strip()

# if __name__ == "__main__":
#     print(f" Reading raw text from '{PDF_FILE_PATH}'...\n")
#     raw_text = extract_text(PDF_FILE_PATH)
    
#     # Print the raw extracted text so you can inspect it
#     print(raw_text)
    
#     # Save the extracted text to a .txt file so Groq can use it in Step 2
#     output_txt = "playground/extracted_text.txt"
#     with open(output_txt, "w", encoding="utf-8") as f:
#         f.write(raw_text)
        
#     print("\n" + "="*50)
#     print(f" Success! Raw text extracted and saved to: {output_txt}")
#     print("="*50)

# Version 3
PDF_FILE_PATH = "playground/dummyResume/resume_test_v1.pdf"

def extract_text_smart(pdf_path: str) -> str:
    """
    Extracts text from a PDF while preserving column reading order.
    Handles single-column and multi-column (Canva-style) layouts cleanly.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: Cannot find file at '{pdf_path}'")
        exit(1)

    full_text = ""
    with pymupdf.open(pdf_path) as doc:
        print(f"📄 Found PDF with {len(doc)} page(s).")
        
        for page_num, page in enumerate(doc):
            full_text += f"\n--- PAGE {page_num + 1} ---\n"
            
            # Extract blocks: (x0, y0, x1, y1, text, block_no, block_type)
            # block_type 0 = text, 1 = image
            blocks = page.get_text("blocks")
            text_blocks = [b for b in blocks if b[6] == 0]

            # Determine page width to distinguish columns
            page_width = page.rect.width
            
            # Check if this looks like a multi-column layout
            # If blocks are split distinctly across the middle:
            left_blocks = [b for b in text_blocks if b[0] < page_width * 0.40]
            right_blocks = [b for b in text_blocks if b[0] >= page_width * 0.40]

            # If it's a clear 2-column layout (both columns have substantial content)
            if len(left_blocks) > 2 and len(right_blocks) > 2:
                # Sort each column individually from top to bottom (y0 coordinate)
                left_blocks.sort(key=lambda b: b[1])
                right_blocks.sort(key=lambda b: b[1])
                
                # Combine: Left column first, then Right column
                sorted_blocks = left_blocks + right_blocks
            else:
                # Standard single-column resume: Sort top-to-bottom, left-to-right
                sorted_blocks = sorted(text_blocks, key=lambda b: (b[1], b[0]))

            # Join the text from sorted blocks
            for b in sorted_blocks:
                content = b[4].strip()
                if content:
                    full_text += content + "\n\n"

    return full_text.strip()

if __name__ == "__main__":
    print(f"Reading and sorting layout from '{PDF_FILE_PATH}'...\n")
    cleaned_text = extract_text_smart(PDF_FILE_PATH)
    
    print(cleaned_text)
    
    # Save the properly structured text
    output_txt = "playground/extracted_text.txt"
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(cleaned_text)
        
    print("\n" + "="*50)
    print(f"Clean column-sorted text saved to: {output_txt}")
    print("="*50)