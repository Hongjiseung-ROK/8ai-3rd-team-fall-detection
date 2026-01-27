import cv2
import cv2.aruco as aruco
import numpy as np

def create_marker_strip(diameter_mm, marker_size_mm, dpi=300):
    """
    원통의 지름에 맞춰 ArUco 마커 띠를 생성하는 함수
    :param diameter_mm: 원통의 지름 (밀리미터)
    :param marker_size_mm: 개별 마커의 한 변 길이 (밀리미터)
    :param dpi: 인쇄 해상도 (보통 300)
    """
    # 1. 물리적 수치 계산
    circumference_mm = np.pi * diameter_mm
    
    # 마커 사이의 최소 간격 (마커 크기의 20%로 설정)
    min_gap_mm = marker_size_mm * 0.2
    
    # 띠 하나에 들어갈 수 있는 최대 마커 개수 계산
    # (마커크기 + 간격) * 개수 <= 원주
    num_markers = int(circumference_mm / (marker_size_mm + min_gap_mm))
    
    if num_markers < 3:
        print("경고: 원통이 너무 얇거나 마커가 너무 큽니다. 최소 3개 이상의 마커가 권장됩니다.")
    
    # 실제 적용될 간격 재계산 (남는 공간을 균등 분배)
    total_gap_mm = circumference_mm - (num_markers * marker_size_mm)
    gap_mm = total_gap_mm / num_markers
    
    print(f"설계 정보: 지름 {diameter_mm}mm 원통에 {marker_size_mm}mm 마커 {num_markers}개를 배치합니다.")
    print(f"마커 간격: {gap_mm:.2f}mm")

    # 2. 픽셀 단위 변환 (mm -> pixel)
    mm_to_px = dpi / 25.4
    marker_px = int(marker_size_mm * mm_to_px)
    gap_px = int(gap_mm * mm_to_px)
    strip_width_px = int(circumference_mm * mm_to_px)
    strip_height_px = int((marker_size_mm + 10) * mm_to_px) # 위아래 여백 5mm씩

    # 3. 빈 이미지 생성 (흰색 배경)
    strip_img = np.ones((strip_height_px, strip_width_px), dtype=np.uint8) * 255
    
    # ArUco 사전 로드
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    
    # 4. 마커 생성 및 배치
    current_x = gap_px // 2 # 첫 번째 마커 시작 위치 (간격의 절반)
    
    # 상하 중앙 정렬을 위한 Y 좌표
    y_offset = (strip_height_px - marker_px) // 2

    for i in range(num_markers):
        # 마커 이미지 생성 (ID는 0부터 순차 증가)
        # borderBits=1 은 마커 테두리 두께
        marker = aruco.generateImageMarker(aruco_dict, id=i, sidePixels=marker_px, borderBits=1)
        
        # 띠 이미지에 마커 붙여넣기
        strip_img[y_offset : y_offset+marker_px, current_x : current_x+marker_px] = marker
        
        # 다음 위치로 이동
        current_x += marker_px + gap_px
        
    return strip_img

if __name__ == "__main__":
    # --- 실행 설정 ---
    print("=== ArUco Marker Strip Generator for Cylinders ===")
    try:
        dia_input = input("원통의 지름을 입력하세요 (mm단위, 예: 60): ")
        CYLINDER_DIAMETER = float(dia_input)
        
        # 마커 크기는 지름의 약 25% 정도로 자동 제안하거나 입력받을 수 있음.
        # 여기서는 기본값 15mm 사용하되, 지름이 너무 작으면 줄임.
        default_size = 15
        if CYLINDER_DIAMETER < 40:
             default_size = 10
        
        size_input = input(f"마커 한 변의 크기를 입력하세요 (mm단위, 엔터치면 기본값 {default_size}mm): ")
        if size_input.strip() == "":
            MARKER_SIZE = default_size
        else:
            MARKER_SIZE = float(size_input)
            
    except ValueError:
        print("잘못된 입력입니다. 숫자를 입력해주세요.")
        exit(1)

    img = create_marker_strip(CYLINDER_DIAMETER, MARKER_SIZE)
    outfile = f"strip_d{int(CYLINDER_DIAMETER)}mm.png"
    cv2.imwrite(outfile, img)
    print(f"[SUCCESS] 이미지 저장 완료: {outfile}")
    print(f"이 이미지를 인쇄하여 지름 {CYLINDER_DIAMETER}mm 원통에 두르세요.")
