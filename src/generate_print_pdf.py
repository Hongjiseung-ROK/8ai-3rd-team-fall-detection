from fpdf import FPDF
import os
import sys
import numpy as np

def create_printable_pdf(image_path, output_pdf_name, target_width_mm, target_height_mm):
    """
    이미지를 A4 PDF에 원본 크기(mm) 그대로 배치하여 저장합니다.
    Center the image on the page.
    """
    # A4 Size
    A4_W_MM = 210
    A4_H_MM = 297
    MARGIN = 10 
    
    # Determine Orientation
    # If width + margins > A4 Width (Portrait), try Landscape
    if target_width_mm + (MARGIN * 2) > A4_W_MM:
        orientation = 'L'
        page_w = A4_H_MM # 297
        page_h = A4_W_MM # 210
        print(f"[INFO] 너비({target_width_mm:.1f}mm)가 커서 가로 모드(Landscape)로 설정합니다.")
    else:
        orientation = 'P'
        page_w = A4_W_MM # 210
        page_h = A4_H_MM # 297
        
    pdf = FPDF(orientation=orientation, unit='mm', format='A4')
    pdf.set_auto_page_break(False) # Disable auto page break to prevent unwanted shifts
    pdf.add_page()
    
    # Check if it fits
    if target_width_mm > page_w or target_height_mm > page_h:
        print(f"[WARNING] 이미지가 용지보다 큽니다! (Image: {target_width_mm:.1f}x{target_height_mm:.1f} mm, Page: {page_w}x{page_h} mm)")
    
    # Calculate Centered Position
    x_pos = (page_w - target_width_mm) / 2
    y_pos = (page_h - target_height_mm) / 2
    
    # Validate negative position (just in case)
    if x_pos < 0: x_pos = 0
    if y_pos < 0: y_pos = 0

    # Image placement
    # w, h explicitly set to ensure physical size match
    pdf.image(image_path, x=x_pos, y=y_pos, w=target_width_mm, h=target_height_mm)
    
    # Draw a reference bounding box (optional, for verification)
    # pdf.rect(x_pos, y_pos, target_width_mm, target_height_mm) 
    
    pdf.output(output_pdf_name)
    print(f"[SUCCESS] PDF 생성 완료: {output_pdf_name}")
    print(f" - Page Size: {page_w}x{page_h} mm (A4 {orientation})")
    print(f" - Image Size: {target_width_mm:.1f}x{target_height_mm:.1f} mm")
    print(f" - Position: x={x_pos:.1f}, y={y_pos:.1f} mm")
    print("주의: 인쇄 시 '페이지 배율 없음(Actual Size)'을 선택해야 정확한 크기로 나옵니다.")

if __name__ == "__main__":
    print("=== ArUco Marker to PDF Converter (Exact A4) ===")
    
    # CLI Support
    # Usage: python src/generate_print_pdf.py [image_path] [diameter_mm] [marker_size_mm]
    if len(sys.argv) == 4:
        img_filename = sys.argv[1]
        dia_input = sys.argv[2]
        size_input = sys.argv[3]
        
        try:
            cy_diameter = float(dia_input)
            marker_size = float(size_input)
        except ValueError:
            print("[ERROR] 숫자를 입력해주세요.")
            exit(1)
            
    else:
        # Interactive Mode
        try:
            img_filename = input("이미지 파일명을 입력하세요 (예: strip_d60mm.png): ").strip()
            if not os.path.exists(img_filename):
                print(f"[ERROR] 파일이 존재하지 않습니다: {img_filename}")
                exit(1)
                
            dia_input = input("원통의 지름을 입력하세요 (mm단위, 예: 60): ")
            cy_diameter = float(dia_input)
            
            size_input = input("마커 한 변의 크기를 입력하세요 (mm단위, 예: 15): ")
            marker_size = float(size_input)
            
        except ValueError:
            print("잘못된 입력입니다. 숫자를 입력해주세요.")
            exit(1)

    # 계산된 실제 출력 크기
    real_width_mm = np.pi * cy_diameter
    real_height_mm = marker_size + 10 # 위아래 여백 포함했던 높이 (generate_cylinder_marker.py 로직 참조)
    
    output_pdf = f"print_{os.path.splitext(img_filename)[0]}.pdf"
    
    create_printable_pdf(img_filename, output_pdf, real_width_mm, real_height_mm)
