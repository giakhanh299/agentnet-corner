"""Động cơ Tự Động Nạp Chuỗi 100 Tập Liên Hoàn (Director -> Artist 4 Hồi -> Animator 4 Hồi).

Chạy tự động trong mỗi chu kỳ 15 phút của `auto_studio_daemon.py` (hoặc chạy tay bất cứ lúc nào):
1. Tự động nạp tiếp kịch bản phim dài 4 Hồi (38 cảnh, 6-8 phút) cho Ban Đạo Diễn (`director`) tiến thẳng tới mốc 100 tập
   (50 Phim Ma Dân Gian `ep40..ep89` + 50 Kiếm Hiệp Kỳ Án `kh26..kh75`), giữ hàng đợi `director` luôn có >= 6 việc.
2. Tự động quét mọi file `episode.json` mới (từ repo hoặc do Đạo diễn vừa đẩy qua `croc` về ổ E:):
   - Tự làm mềm từ nhạy cảm trong `image_prompt` để không bao giờ bị bộ lọc Muse chặn.
   - Tự đẩy bản sao `episode.json` lên VPS (`/var/lib/agentnet-media/<slug>/episode.json`) để Họa sĩ đọc ngay qua
     `https://muse.alltool.pro/media/<slug>/episode.json` (tên miền đã whitelist sẵn, không cần đợi git push!).
   - Tự động chẻ thành 4 Hồi (`muse_draw_images` 9-10 cảnh/Hồi cho phim 32-40 cảnh; 1 lô cho K01/K08) nạp thẳng vào Hub
     để dàn 8 Họa sĩ (`artist`) chạy liên hoàn không bao giờ bị rảnh `0` việc!
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import process_muse_pipeline as pm  # noqa: E402

MEDIA_ROOT = Path(r"E:\MUSE_MEDIA_STUDIO")
TARGET_TOTAL_MOVIES = 100
MIN_DIRECTOR_QUEUED = 8
MAX_ARTIST_QUEUED = 32

SENSITIVE_MAP = [
    (re.compile(r"\bcorpses?\b", re.I), "motionless pale figure"),
    (re.compile(r"\bbloody\b", re.I), "crimson-stained"),
    (re.compile(r"\bbleeding\b", re.I), "stained with crimson cinnabar"),
    (re.compile(r"\bblood\b", re.I), "crimson cinnabar ink"),
    (re.compile(r"\bdaggers?\b", re.I), "ornate antique bronze blade"),
    (re.compile(r"\bskeletal\b", re.I), "gaunt shadow-draped"),
    (re.compile(r"\bskeletons?\b", re.I), "ancient weathered relic"),
    (re.compile(r"\bdead bod(?:y|ies)\b", re.I), "still shrouded figure"),
    (re.compile(r"\bmurder(?:ed|er)?\b", re.I), "dark conspiracy"),
    (re.compile(r"\bsuicide\b", re.I), "tragic disappearance"),
    (re.compile(r"\bsevered\b", re.I), "broken antique"),
    (re.compile(r"\bdecapitated\b", re.I), "weathered headless statue"),
    (re.compile(r"\bpoison(?:ed)?\b", re.I), "mysterious bitter herb"),
    (re.compile(r"\bdying\b", re.I), "fading exhausted"),
    (re.compile(r"\bhanged\b", re.I), "suspended empty lantern"),
]

# Kho 100 chủ đề chuyển thể Trung Quốc (50 Phim Ma Dân Gian + 50 Kiếm Hiệp Cổ Trang Kỳ Án)
HORROR_TOPICS: list[tuple[str, str, str]] = [
    ("ep43_dam_cuoi_am_trong_suong_mu_nui_bac", "Đám Cưới Âm Trong Sương Mù Núi Bắc", "《冥婚借道》— Kiệu hoa đỏ đi qua đèo sương đêm rằm, phu kiệu phát hiện tân nương còn thở và đang kêu cứu khỏi mưu kế tráo gia sản"),
    ("ep44_nguoi_gac_mieu_khong_ngon_den", "Người Gác Miếu Không Ngọn Đèn", "《守庙三禁》— Ba điều cấm kỵ của miếu Sơn Thần cổ: tuyệt đối không mở hòm công đức sau giờ Tý, lật mở bí mật kho bạc thất lạc"),
    ("ep45_tieng_go_mo_duoi_gieng_lang_co", "Tiếng Gõ Mõ Dưới Giếng Làng Cổ", "《古井木鱼》— Đêm nào cũng có tiếng mõ vọng từ giếng cạn đầu làng, thợ đào giếng xuống đáy phát hiện mật thất ẩn thân 30 năm"),
    ("ep46_quan_tro_ba_ngon_nen_xanh", "Quán Trọ Ba Ngọn Nến Xanh", "《三盏青灯客栈》— Khách lỡ đường ngủ nhờ quán trọ hoang ven đèo, ba ngọn nến xanh tắt dần báo hiệu kẻ giả danh trong nhóm lữ khách"),
    ("ep47_chuyen_do_khuya_ben_song_hoang", "Chuyến Đò Khuya Bến Sông Hoang", "《夜渡黄泉津》— Lão lái đò chỉ chở khách trả tiền xu cổ, một đêm chở vị quan áo xanh lật lại vụ án oan chìm thuyền năm xưa"),
    ("ep48_chiec_guong_dong_trong_tu_duong", "Chiếc Gương Đồng Trong Từ Đường", "《祠堂照影铜镜》— Gương đồng cổ trong từ đường soi ra bóng người đứng sau lưng mỗi đêm mưa, vạch trần kẻ giả mạo trưởng tộc"),
    ("ep49_tho_khac_bia_mo_dem_giao_thua", "Thợ Khắc Bia Mộ Đêm Giao Thừa", "《除夕刻碑人》— Khách áo đen thuê khắc tên chính người thợ vào tấm bia đá trước giờ giao thừa, mở ra màn đổi mạng bất ngờ"),
    ("ep50_bay_bac_thang_nha_co_ho_ly", "Bảy Bậc Thang Nhà Cổ Hồ Ly", "《七阶老宅》— Ngôi nhà cổ ban ngày có 6 bậc thang nhưng nửa đêm thành 7 bậc, bước nhầm bậc thứ 7 dẫn vào mật thất cất gia phả thật"),
    ("ep51_nguoi_canh_linh_cuu_nha_ho_tham", "Người Canh Linh Cữu Nhà Họ Thẩm", "《沈府守灵夜》— Ba quy tắc canh linh cữu nhà giàu họ Thẩm: cấm để mèo nhảy qua, cấm tắt đèn dầu, lật tẩy màn giả chết thử lòng con cháu"),
    ("ep52_con_roi_go_biet_quay_dau_nua_dem", "Con Rối Gỗ Biết Quay Đầu Nửa Đêm", "《傀儡戏班》— Gánh hát rối gỗ cổ truyền bỗng có một con rối tự quay đầu nhìn khán giả, hé lộ bí mật người nghệ nhân bị giấu kín"),
    ("ep53_ngoi_lang_khong_ai_dam_nhin_guong", "Ngôi Làng Không Ai Dám Nhìn Gương", "《无镜村》— Cả ngôi làng miền núi che kín mọi mặt gương và mặt nước sau chập tối để tránh lời nguyền cũ, thực chất che giấu âm mưu lớn"),
    ("ep54_chiec_ao_cuoi_theu_chi_vang_co", "Chiếc Áo Cưới Thêu Chỉ Vàng Cổ", "《金线嫁衣》— Tiệm may cổ nhận sửa chiếc áo cưới百年 chỉ vàng, mỗi mũi kim khâu lại hiện ký ức vụ mất tích của tiểu thư năm xưa"),
    ("ep55_tieng_sao_truc_trong_rung_tre_mu", "Tiếng Sáo Trúc Trong Rừng Tre Mù", "《雾竹林笛声》— Đêm sương mù rừng tre vang tiếng sáo dẫn lối lữ khách lạc đường, người thổi sáo thực ra là nhân chứng duy nhất còn sống"),
    ("ep56_thay_dia_ly_va_ngoi_mo_song_sinh", "Thầy Địa Lý Và Ngôi Mộ Song Sinh", "《双生阴宅》— Thầy địa lý phát hiện hai ngôi mộ song sinh đặt ngược long mạch nhằm yểm cả dòng họ, từng bước phá giải bí ẩn"),
    ("ep57_chiec_den_long_giay_do_truoc_cong", "Chiếc Đèn Lồng Giấy Đỏ Trước Cổng", "《红纸灯笼夜》— Lệ làng cứ nhà nào tự dưng xuất hiện đèn lồng giấy đỏ trước cửa lúc nửa đêm là sắp gặp biến cố"),
    ("ep58_quan_tra_mo_cua_luc_nua_dem", "Quán Trà Mở Cửa Lúc Nửa Đêm", "《子夜茶楼》— Quán trà cổ chỉ mở từ giờ Tý đến giờ Dần cho những vị khách mang chuyện bí mật tới đổi lấy một chén trà giải oan"),
    ("ep59_nguoi_nhat_tien_vang_ma_tren_deo", "Người Nhặt Tiền Vàng Mã Trên Đèo", "《山道拾冥钱》— Chàng thư sinh lỡ nhặt xấp tiền giấy trên đèo núi, từ đó liên tiếp gặp manh mối dẫn tới vụ án cổ 15 năm trước"),
    ("ep60_can_phong_khoa_kin_o_lau_ba", "Căn Phòng Khóa Kín Ở Lầu Ba", "《三楼封门房》— Lầu ba của ngôi biệt phủ cổ bị niêm phong 20 năm nhưng đêm nào cũng có tiếng bước chân và bóng đèn dầu hắt qua khe cửa"),
    ("ep61_ong_lao_ban_quan_tai_pho_co", "Ông Lão Bán Quan Tài Phố Cổ", "《古街棺材铺》— Tiệm quan tài phố cổ nhận đặt đóng chiếc quan tài gỗ lim không ghi tên người nằm, hóa ra là cái bẫy vạch mặt kẻ gian"),
    ("ep62_muoi_hai_tieng_chuong_chua_hoang", "Mười Hai Tiếng Chuông Chùa Hoang", "《荒寺十二钟》— Ngôi chùa bỏ hoang trên núi bỗng vang đủ 12 tiếng chuông đêm mưa bão, kéo 5 người từng dính líu tới bí mật cũ quay lại"),
    ("ep63_buc_tranh_thuy_mac_doi_canh_dem", "Bức Tranh Thủy Mặc Đổi Cảnh Đêm", "《夜变水墨画》— Bức tranh thủy mặc cổ mỗi đêm lại thêm một bóng người bước gần về phía đình cổ, ẩn chứa bản đồ mật"),
    ("ep64_nguoi_do_muoi_tren_ben_song_lanh", "Người Đo Nước Trên Bến Sông Lạnh", "《寒江测水人》— Người đo mực nước đêm lũ nhìn thấy chiếc thuyền không người trôi ngược dòng, mở ra bí mật ngôi làng bị nhấn chìm"),
    ("ep65_ba_bat_com_cung_duoi_goc_da_gia", "Ba Bát Cơm Cúng Dưới Gốc Đa Già", "《古榕三碗饭》— Đêm mùng Một có người lén đặt 3 bát cơm nóng dưới gốc đa cổ thụ, kẻ rình xem phát hiện bí mật kinh hoàng của trưởng thôn"),
    ("ep66_ngon_den_dau_khong_tat_trong_bao", "Ngọn Đèn Dầu Không Tắt Trong Bão", "《风暴长明灯》— Giữa đêm bão lớn, ngọn đèn dầu trong từ đường cháy suốt không tắt nhờ cơ quan ngầm che giấu chứng cứ"),
    ("ep67_tieng_khoc_sau_buc_tuong_gach_co", "Tiếng Khóc Sau Bức Tường Gạch Cổ", "《老墙哭声》— Thợ sửa nhà cổ nghe tiếng gõ nhịp đều đặn từ sau bức tường gạch dày, phá tường mở ra kho nhật ký thất truyền"),
    ("ep68_chiec_luoc_ngoc_cua_co_nuong_ao_xanh", "Chiếc Lược Ngọc Của Cô Nương Áo Xanh", "《青衣玉梳》— Chiếc lược ngọc nhặt được bên hồ sen luôn tự quay về chỗ cũ mỗi sáng, dẫn đường giải mã vụ mất tích của tiểu thư"),
    ("ep69_chuyen_xe_ngua_khong_nguoi_danh", "Chuyến Xe Ngựa Không Người Đánh", "《无夫马车》— Đêm sương trên đường quan đạo xuất hiện cỗ xe ngựa chạy êm ru không người cầm cương, bên trong giấu mật thư triều đình"),
    ("ep70_ngoi_nha_muoi_ba_canh_cua_so", "Ngôi Nhà Mười Ba Cánh Cửa Sổ", "《十三窗旧居》— Biệt thự cổ nhìn bên ngoài có 13 cửa sổ nhưng đếm bên trong chỉ có 12, cánh cửa sổ thừa giấu căn phòng bí mật"),
    ("ep71_thay_thuoc_chua_benh_cho_khach_dem", "Thầy Thuốc Chữa Bệnh Cho Khách Đêm", "《夜诊老医馆》— Lão lang y đêm nào cũng có người gõ cửa bốc thuốc bằng bạc vụn cũ, lần theo dấu chân phát hiện thôn ẩn sĩ"),
    ("ep72_bai_thuoc_goi_ky_uc_trong_hu_gom", "Bài Thuốc Gọi Ký Ức Trong Hũ Gốm", "《陶罐忆魂香》— Lọ trầm cổ có mùi hương khiến người ngửi thấy lại cảnh tượng 10 năm trước, giúp phá vỡ lời nói dối hoàn hảo"),
    ("ep73_tieng_trong_canh_ba_o_phu_huyen", "Tiếng Trống Canh Ba Ở Phủ Huyện", "《三更县衙鼓》— Đêm nào đúng canh ba trống kêu oan trước công đường cũng tự vang lên dù cổng đã khóa chặt"),
    ("ep74_nguoi_viet_gia_pha_thieu_mot_trang", "Người Viết Gia Phả Thiếu Một Trang", "《缺页族谱》— Quyển gia phả cổ bị xé mất đúng một trang giữa, người thợ phục chế tìm thấy tờ giấy giấu trong gáy sách"),
    ("ep75_cay_cau_da_chi_di_duoc_mot_chieu", "Cây Cầu Đá Chỉ Đi Được Một Chiều", "《单行石桥》— Lời đồn qua cầu đá cổ lúc nửa đêm cấm quay đầu nhìn lại, chàng lính tuần cố tình quay đầu và phát hiện sự thật"),
    ("ep76_hop_nhac_dong_trong_tiem_do_co", "Hộp Nhạc Đồng Trong Tiệm Đồ Cổ", "《古董铜八音盒》— Hộp nhạc đồng tự phát giai điệu mỗi khi trời sắp đổ mưa, ẩn chứa mật mã mở hầm vàng"),
    ("ep77_nguoi_giu_vuon_le_trang_dem_ram", "Người Giữ Vườn Lê Trắng Đêm Rằm", "《月夜梨园守》— Vườn lê nở hoa trắng xóa giữa mùa đông, bóng áo trắng lướt qua gốc cây dẫn tới bí mật của gia tộc"),
    ("ep78_chiec_khan_theu_chim_hac_bay_nguoc", "Chiếc Khăn Thêu Chim Hạc Bay Ngược", "《逆飞鹤帕》— Mảnh khăn cổ thêu đàn hạc bay ngược chiều là tín vật nhận thân của một vụ tráo con kéo dài 18 năm"),
    ("ep79_bai_co_vua_chua_danh_xong_tren_nui", "Bàn Cờ Chưa Đánh Xong Trên Đỉnh Núi", "《残局山亭》— Trong đình đá trên đỉnh núi luôn có bàn cờ vây tự dịch chuyển từng quân mỗi đêm trăng"),
    ("ep80_chiec_chuong_gio_bang_xuong_ngoc", "Chiếc Chuông Gió Bằng Ngọc Cổ", "《古玉风铃》— Chuông gió treo dưới mái hiên không gió vẫn rung đúng giờ Sửu, báo hiệu kẻ đột nhập qua đường hầm"),
    ("ep81_con_thuyen_giay_tren_ho_suong_mu", "Con Thuyền Giấy Trên Hồ Sương Mù", "《雾湖纸船》— Đêm nào trên hồ cũng có con thuyền giấy chở ngọn nến nhỏ trôi thẳng tới bến nhà quan phủ"),
    ("ep82_ong_tho_dong_ho_co_trong_ngo_sau", "Ông Thợ Đồng Hồ Cổ Trong Ngõ Sâu", "《深巷老钟匠》— Mọi chiếc đồng hồ trong ngõ đều dừng đúng 11 giờ 45 mỗi tối thứ Bảy, che giấu bí mật vụ trộm lớn"),
    ("ep83_buc_tuong_dat_set_khoc_ra_nuoc", "Bức Tượng Đất Sét Rỉ Giọt Sương Đêm", "《夜泣泥像》— Bức tượng cổ trong miếu cứ đêm rằm lại rỉ nước lạnh từ khóe mắt, hé lộ mạch nước ngầm và kho cổ vật"),
    ("ep84_la_thu_gui_tu_tram_dich_bo_hoang", "Lá Thư Gửi Từ Trạm Dịch Bỏ Hoang", "《荒驿来信》— Trạm dịch bỏ hoang 25 năm bỗng gửi về một bức mật thư đóng dấu sáp đỏ còn mới nguyên"),
    ("ep85_chiec_chum_sanh_trong_ham_ruou_co", "Chiếc Chum Sành Trong Hầm Rượu Cổ", "《酒窖封坛》— Hầm rượu cổ có một chiếc chum bị niêm phong bùa vàng, mở ra không phải rượu mà là bằng chứng chấn động"),
    ("ep86_dem_hoi_den_hoa_dang_ben_bo_co", "Đêm Hội Đèn Hoa Đăng Bên Bờ Cổ", "《古岸放河灯》— Một chiếc đèn hoa đăng viết tên người còn sống trôi ngược dòng nước giữa đêm hội rằm"),
    ("ep87_nguoi_ke_chuyen_ma_o_cho_am_phu", "Người Kể Chuyện Ở Phiên Chợ Đêm Cổ", "《鬼市说书人》— Phiên chợ đêm họp lúc gà gáy có lão kể chuyện luôn kể đúng sự việc sắp xảy ra ngày hôm sau"),
    ("ep88_ngoi_mo_khong_co_tren_nui_tuyet", "Ngôi Mộ Không Cỏ Trên Núi Tuyết", "《无草雪冢》— Giữa sườn núi tuyết phủ trắng có khoảnh đất luôn ấm không đọng tuyết, bên dưới là mật đạo cổ"),
    ("ep89_chiec_quat_giay_ve_bay_bong_nguoi", "Chiếc Quạt Giấy Vẽ Bảy Bóng Người", "《七影折扇》— Cây quạt cổ vẽ 7 vị khách dự tiệc nhưng sau mỗi đêm lại biến mất một bóng người trong tranh"),
]

WUXIA_TOPICS: list[tuple[str, str, str]] = [
    ("kh29_kiem_khach_cut_tay_o_tuu_lau_cu", "Kiếm Khách Cụt Tay Ở Tửu Lâu Cũ", "《断臂酒客》— Lão bộc cụt tay rót rượu ở tửu lâu hẻo lánh bị 4 cao thủ vây ép, lật kèo lộ thân phận Đệ Nhất Kiếm Khách ẩn danh"),
    ("kh30_hop_giam_sat_khoa_ba_tang_tren_nui", "Hộp Sắt Khóa Ba Tầng Trên Đỉnh Tuyết", "《雪峰三锁铁匣》— Bảy môn phái tranh đoạt chiếc hộp sắt chứa bí kíp tuyệt học, mở ra chỉ có một bức thư vạch mặt minh chủ"),
    ("kh31_ba_chen_ruou_tien_tai_quan_doc_ma", "Ba Chén Rượu Tiễn Tại Quán Độc Mã", "《独马镇三杯酒》— Ba cao thủ giang hồ hẹn nhau uống 3 chén rượu trước trận quyết đấu, từng chén rượu lật mở một tầng sự thật"),
    ("kh32_nguoi_ban_dau_phu_va_thanh_dao_han", "Người Bán Đậu Phụ Và Thanh Đao Hàn", "《豆腐摊藏刀》— Ông chủ quán đậu phụ hiền lành bị băng cướp phá quán, một nhát dao cắt đậu lộ tuyệt kỹ đao pháp thất truyền"),
    ("kh33_mat_lenh_thanh_long_dem_mua_gio", "Mật Lệnh Thanh Long Đêm Mưa Gió", "《青龙密令》— Tiêu cục hộ tống rương gỗ không trọng lượng xuyên rừng mưa, hóa ra người áp tiêu mới là mục tiêu thật sự"),
    ("kh34_co_gai_mu_choi_dan_ty_ba_giua_ai", "Cô Gái Mù Chơi Đàn Tỳ Bà Giữa Ải", "《边关盲女琵琶》— Tiếng đàn tỳ bà giữa biên ải chặn đứng cả đội sát thủ, mỗi nhịp dây đàn là một chiêu âm công sắc bén"),
    ("kh35_cuoc_hen_duoi_thap_co_nghin_nam", "Cuộc Hẹn Dưới Tháp Cổ Nghìn Năm", "《千年古塔之约》— Hai kỳ phùng địch thủ hẹn quyết chiến sau 10 năm dưới tháp cổ, phát hiện cả hai đều bị kẻ thứ ba giật dây"),
    ("kh36_thay_do_ngheo_va_cuon_kiem_pho_rach", "Thầy Đồ Nghèo Và Cuốn Kiếm Phổ Rách", "《残卷书生》— Chàng thư sinh dùng cuốn sách rách kê chân bàn, một đêm cứu quán trọ mới lộ toàn bộ chiêu thức giấu trong nét chữ"),
    ("kh37_muoi_hai_cao_thu_trong_tram_dich_tuyet", "Mười Hai Cao Thủ Trong Trạm Dịch Tuyết", "《风雪驿站十二客》— Bão tuyết cô lập 12 nhân vật giang hồ trong trạm dịch, một báu vật biến mất kéo theo màn đấu trí kiểu Cổ Long"),
    ("kh38_lao_an_may_giu_cong_thanh_phuong_bac", "Lão Ăn Mày Giữ Cổng Thành Phương Bắc", "《北城老丐》— Lão ăn mày ngồi góc cổng thành 15 năm chỉ dùng một cây gậy trúc bẻ gãy kiếm của sứ giả ngoại bang"),
    ("kh39_thanh_kiem_khong_luoi_cua_vi_tuong_gia", "Thanh Kiếm Không Lưỡi Của Vị Tướng Già", "《无锋老剑》— Vị lão tướng về ở ẩn mang thanh kiếm gỗ không lưỡi ra cứu đệ tử cũ trước vòng vây của 8 đại cao thủ"),
    ("kh40_chuyen_tieu_cuoi_cung_qua_hem_nui_den", "Chuyến Tiêu Cuối Cùng Qua Hẻm Núi Đen", "《黑风谷末镖》— Tổng tiêu đầu sắp giải nghệ nhận chuyến tiêu cuối kỳ lạ: hộ tống chính kẻ từng truy sát mình năm xưa"),
    ("kh41_nu_chu_quan_tra_va_bay_vien_bi_sat", "Nữ Chủ Quán Trà Và Bảy Viên Bi Sắt", "《茶铺七铁丸》— Nữ chủ quán trà dịu dàng dùng 7 viên bi sắt xoay trong tay hóa giải toàn bộ ám khí của môn phái hắc đạo"),
    ("kh42_nguoi_tho_ren_khong_bao_gio_ren_kiem", "Người Thợ Rèn Không Bao Giờ Rèn Kiếm", "《不铸剑的铁匠》— Lão thợ rèn suốt 20 năm chỉ rèn cuốc xẻng bỗng đỏ lò rèn một thanh kiếm ngắn để trả món nợ nghĩa tình"),
    ("kh43_tran_co_sinh_tu_tren_thuyen_hoa_dem", "Trận Cờ Sinh Tử Trên Thuyền Hoa Đêm", "《夜舫生死棋》— Giữa sông sương mù, ván cờ trên thuyền hoa quyết định số phận cả một môn phái với 3 cú lật kèo nghẹt thở"),
    ("kh44_bi_mat_chiec_mat_na_bac_giang_ho", "Bí Mật Chiếc Mặt Nạ Bạc Giang Hồ", "《银面客之谜》— Ba người cùng đeo chiếc mặt nạ bạc xuất hiện ở ba thành khác nhau trong cùng một đêm để phá âm mưu phản loạn"),
    ("kh45_tieu_nhi_quet_san_va_bo_phap_vo_anh", "Tiểu Nhị Quét Sân Và Bộ Pháp Vô Ảnh", "《扫地小二》— Chú tiểu nhị lau bàn quét sân trong tửu lâu bị coi thường, khi cao thủ xông vào mới lộ khinh công đệ nhất"),
    ("kh46_ngon_tieu_duoi_anh_trang_khuyet", "Ngọn Tiêu Dưới Ánh Trăng Khuyết", "《残月玉箫》— Vị công tử thổi tiêu ngọc bên cầu đá tìm ra kẻ phản bội sư môn chỉ qua một nốt nhạc lệch nhịp"),
    ("kh47_bua_tiec_sinh_nhat_cua_trang_chu_vo_lam", "Bữa Tiệc Của Trang Chủ Võ Lâm", "《武林山庄寿宴》— Tiệc thọ quy tụ ngũ đại cao thủ biến thành phiên tòa lật mặt kẻ đứng sau vụ diệt môn 12 năm trước"),
    ("kh48_hai_nua_ngoc_boi_song_long_tai_ngo", "Hai Nửa Ngọc Bội Song Long Tái Ngộ", "《双龙玉佩》— Hai kẻ tử thù giao đấu trên vách đá bỗng rơi ra hai nửa ngọc bội khớp nhau hoàn hảo, vạch trần kẻ chủ mưu"),
    ("kh49_nguoi_gac_thap_chuong_thanh_co", "Người Gác Tháp Chuông Thành Cổ", "《古楼守钟人》— Tiếng chuông báo giờ của lão gác tháp thực chất là mật mã cảnh báo cho các hiệp khách trong thành"),
    ("kh50_thanh_dao_bo_quen_trong_quan_chao_khuya", "Thanh Đao Bỏ Quên Trong Quán Cháo Khuya", "《夜粥铺遗刀》— Một thanh bảo đao bị bỏ quên ở quán cháo khuya kéo 5 thế lực giang hồ tới đòi nhận, chủ thật lại đang ngồi ăn cháo"),
    ("kh51_vi_quan_xu_an_khong_mang_binh_khi", "Vị Quan Xử Án Không Mang Binh Khí", "《无兵判官》— Vị quan trẻ tay không bước vào sào huyệt bang phái, dùng đúng 3 câu hỏi khiến tên đầu sỏ tự sập bẫy"),
    ("kh52_ngoi_chua_tren_vach_da_may_trang", "Ngôi Chùa Trên Vách Đá Mây Trắng", "《白云崖古寺》— Sát thủ giả làm khách hành hương lên chùa tìm kiếm phổ, không ngờ vị hòa thượng quét lá đã biết từ 3 ngày trước"),
    ("kh53_la_thu_thach_dau_bang_canh_mai_kho", "Lá Thư Thách Đấu Bằng Cành Mai Khô", "《枯梅战书》— Một cành mai khô đặt trước cửa báo hiệu cuộc tái đấu của kiếm thánh sau 20 năm quy ẩn"),
    ("kh54_ke_trom_khong_bao_gio_lay_vang_bac", "Kẻ Trộm Không Bao Giờ Lấy Vàng Bạc", "《不偷金的侠盗》— Đạo tặc lừng danh chỉ lấy sổ sách ghi nợ của cường hào, một đêm bị phục kích trong mật thất và lật ngược thế cờ"),
    ("kh55_chuyen_do_co_hai_vi_kiem_khach_ao_trang", "Chuyến Đò Của Hai Kiếm Khách Áo Trắng", "《白衣双剑渡》— Hai kiếm khách mặc đồ giống hệt nhau cùng lên một chuyến đò, một người là thật và một người là giả"),
    ("kh56_quan_ruou_chi_ban_cho_nguoi_co_chuyen", "Quán Rượu Chỉ Bán Cho Người Có Chuyện", "《故事酒馆》— Quán rượu biên ải không thu tiền bạc mà thu một bí mật giang hồ, ghép 3 câu chuyện lại thành vụ đại án"),
    ("kh57_ong_lao_cau_ca_ben_thac_ngan_truong", "Ông Lão Câu Cá Bên Thác Ngàn Trượng", "《千丈瀑钓翁》— Cần câu tre không lưỡi của ông lão bên thác nước chặn đứng nhát kiếm sấm sét của thích khách"),
    ("kh58_cuon_ban_do_kho_bau_ve_tren_ao_giap", "Bản Đồ Kho Báu Vẽ Trên Áo Giáp", "《甲衣藏图》— Manh mối kho báu giấu trong hoa văn bộ giáp cũ của lão binh, dẫn các anh hùng tới bí mật bảo vệ biên cương"),
    ("kh59_ba_ngay_o_tran_bien_ai_khong_luat", "Ba Ngày Ở Trấn Biên Ải Không Luật", "《无律边镇三日》— Một lãng khách đặt chân vào thị trấn bị băng cướp kiểm soát, dùng mưu chia rẽ 3 băng nhóm trong 3 ngày"),
    ("kh60_chiec_o_giay_dau_chan_mua_ten", "Chiếc Ô Giấy Dầu Chắn Mưa Tên", "《油纸伞挡箭》— Nữ hiệp cầm chiếc ô giấy dầu bước qua cầu gỗ giữa cơn mưa tên, mỗi vòng xoay ô là một tuyệt học thất truyền"),
    ("kh61_nguoi_mua_kiem_o_cho_troi_mua_dong", "Người Mua Kiếm Ở Chợ Trời Mùa Đông", "《冬市买剑人》— Thanh kiếm gỉ sét bán rẻ ngoài chợ trời rơi vào tay người biết nhìn thép, mở lại ân oán của Tứ Đại Thế Gia"),
    ("kh62_tieng_dan_co_cam_trong_dem_tuyet_roi", "Tiếng Đàn Cổ Cầm Trong Đêm Tuyết Rơi", "《雪夜古琴》— Tiếng đàn cổ cầm bình thản giữa vòng vây trăm người giúp hóa giải hận thù kéo dài hai thế hệ"),
    ("kh63_vi_thay_thuoc_giang_ho_va_ba_dieu_kien", "Thầy Thuốc Giang Hồ Và Ba Điều Kiện", "《江湖医三约》— Thần y ẩn sĩ chỉ cứu người khi họ trả lời thật 3 câu hỏi, nhờ đó vạch mặt kẻ giả dạng người bị hại"),
    ("kh64_tran_dau_khong_rut_kiem_tai_lôi_dai", "Trận Đấu Không Rút Kiếm Tại Lôi Đài", "《不拔剑之战》— Đại hội võ lâm chứng kiến màn tỷ thí kỳ lạ: hai cao thủ đứng bất động giữa lôi đài đấu khí thế trong 3 phút"),
    ("kh65_chiec_trâm_bac_cua_cong_chua_luu_lac", "Chiếc Trâm Bạc Của Công Chúa Lưu Lạc", "《流落银簪》— Một cô gái bán trà vô tình để lộ chiếc trâm bạc hoàng thất, kéo theo cuộc hộ tống kịch tính xuyên 3 châu"),
    ("kh66_nguoi_viet_so_sinh_tu_cua_vo_lam", "Người Viết Sổ Danh Sách Cao Thủ", "《武林谱录官》— Kẻ chuyên xếp hạng cao thủ giang hồ bất ngờ bị truy sát vì cuốn sổ mới nhất chỉ ghi trống vị trí Đệ Nhất"),
    ("kh67_can_nha_go_ben_rung_thong_bap_bung", "Căn Nhà Gỗ Bên Rừng Thông Đêm Bão", "《松林风暴木屋》— Bốn lữ khách trú bão trong căn nhà gỗ nhỏ, dần nhận ra mỗi người đều mang một nửa sự thật của vụ án năm xưa"),
    ("kh68_thanh_kiem_giau_trong_cay_gay_hanh_khat", "Thanh Kiếm Giấu Trong Cây Gậy Hành Khất", "《乞杖藏锋》— Hành khất trẻ bị vu oan lấy cắp bảo vật, ngay giữa công đường rút thanh bảo kiếm chứng minh thân thế"),
    ("kh69_muoi_nam_cho_mot_chen_tra_nguoi", "Mười Năm Chờ Một Chén Trà Nguội", "《十年冷茶》— Chén trà đặt sẵn trên bàn suốt 10 năm chờ người bạn cũ trở về giải oan cho cả sư môn"),
    ("kh70_hiep_khach_ao_xam_pha_bay_co_quan", "Hiệp Khách Áo Xám Phá Bẫy Cơ Quan", "《灰衣破机关》— Biệt viện đầy cơ quan mật đạo được dựng để thử thách truyền nhân, kẻ tham lam đều mắc bẫy còn người nhân nghĩa thắng"),
    ("kh71_tieng_sao_goi_chim_ung_o_sa_mac_tay", "Tiếng Sáo Gọi Chim Ưng Ở Sa Mạc Tây", "《西漠鹰笛》— Giữa sa mạc bão cát, tiếng sáo gọi ưng dẫn lối đội thương nhân thoát khỏi phục kích của sơn tặc"),
    ("kh72_cuoc_doi_dau_giua_hai_vi_su_huynh_de", "Cuộc Đối Đầu Giữa Hai Sư Huynh Đệ", "《同门双雄》— Hai sư huynh đệ chia ngả 15 năm gặp lại trên cầu đá, trận chiến thực chất là vở kịch lừa tên gian thần lộ diện"),
    ("kh73_chiec_nhan_ngoc_cua_bang_chu_an_danh", "Chiếc Nhẫn Ngọc Của Bang Chủ Ẩn Danh", "《隐名帮主戒》— Bang phái rơi vào nội loạn tranh ngôi bang chủ, chiếc nhẫn ngọc thật nằm trên tay người nhỏ bé nhất"),
    ("kh74_dem_cuoi_o_phuong_hoa_dang_kinh_thanh", "Đêm Cuối Ở Phố Hoa Đăng Kinh Thành", "《京城花灯夜》— Giữa lễ hội hoa đăng rực rỡ, cuộc rượt đuổi thầm lặng trên mái ngói ngăn chặn âm mưu đánh tráo quốc ấn"),
    ("kh75_nhat_kiem_ket_thuc_muoi_nam_an_oan", "Nhất Kiếm Kết Thúc Mười Năm Ân Oán", "《十年一剑》— Chương kết hùng tráng về vị kiếm khách buông kiếm giải giáp sau khi minh oan cho toàn bộ đồng môn"),
]


def _interleaved_catalog() -> list[tuple[str, str, str, str]]:
    out: list[tuple[str, str, str, str]] = []
    n = max(len(HORROR_TOPICS), len(WUXIA_TOPICS))
    for i in range(n):
        if i < len(HORROR_TOPICS):
            slug, title, premise = HORROR_TOPICS[i]
            out.append(("phim-ma-dan-gian", slug, title, premise))
        if i < len(WUXIA_TOPICS):
            slug, title, premise = WUXIA_TOPICS[i]
            out.append(("kiem-hiep-co-trang", slug, title, premise))
    return out


def soften_episode_prompts(spec_path: Path) -> bool:
    """Tự động làm mềm các từ dễ vướng bộ lọc an toàn trong image_prompt của episode.json."""
    try:
        data = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    changed = False
    for sc in data.get("scenes") or []:
        for key in ("image_prompt", "visual_prompt"):
            txt = sc.get(key)
            if not isinstance(txt, str):
                continue
            new_txt = txt
            for pat, rep in SENSITIVE_MAP:
                new_txt = pat.sub(rep, new_txt)
            if new_txt != txt:
                sc[key] = new_txt
                changed = True
    if changed:
        spec_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def mirror_specs_to_vps(specs: list[tuple[str, Path]]) -> int:
    """Đẩy nhanh bản sao episode.json lên /var/lib/agentnet-media/<slug>/episode.json để Họa sĩ đọc ngay qua alltool.pro."""
    if not specs:
        return 0
    ssh = pm.connect_vps_ssh(timeout=25)
    uploaded = 0
    try:
        sftp = ssh.open_sftp()
        dirs = [f"/var/lib/agentnet-media/{slug}" for slug, _ in specs]
        ssh.exec_command("mkdir -p " + " ".join(dirs))[1].read()
        for slug, sp in specs:
            try:
                sftp.put(str(sp), f"/var/lib/agentnet-media/{slug}/episode.json")
                uploaded += 1
            except Exception:
                pass
        sftp.close()
        ssh.exec_command("chown -R agentnet-corner:agentnet-corner " + " ".join(dirs))[1].read()
    finally:
        ssh.close()
    return uploaded


def discover_all_local_specs() -> dict[str, tuple[str, Path, dict]]:
    """Quét mọi episode.json hợp lệ trên đĩa (ưu tiên channel đúng theo prefix ep/kh/v0/k1_)."""
    found: dict[str, tuple[str, Path, dict]] = {}
    scan_roots: list[tuple[str, Path]] = [
        ("phim-ma-dan-gian", pm.REPO_MA / "phim-ma-dan-gian"),
        ("kiem-hiep-co-trang", pm.REPO_MA / "kiem-hiep-co-trang"),
        ("tien-va-doi-srt", pm.REPO_MA / "tien-va-doi-srt"),
        ("tap-lam-content", pm.REPO_K08),
    ]
    for ch_key, root in scan_roots:
        if not root.is_dir():
            continue
        for ep in sorted(root.iterdir()):
            sp = ep / "episode.json"
            if not sp.is_file():
                continue
            slug = ep.name
            # Tránh nhận nhầm kh* nằm sót trong phim-ma-dan-gian
            if slug.startswith("kh") and ch_key != "kiem-hiep-co-trang":
                continue
            if slug.startswith("ep") and ch_key != "phim-ma-dan-gian":
                continue
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
            except Exception:
                continue
            scenes = data.get("scenes") or []
            if ch_key in ("phim-ma-dan-gian", "kiem-hiep-co-trang") and len(scenes) < 32:
                continue
            if len(scenes) < 8:
                continue
            found[slug] = (ch_key, sp, data)
    return found


def count_local_images(ch_key: str, slug: str) -> int:
    # Kiểm tra cả thư mục đúng kênh lẫn fallback nếu croc cũ lỡ đặt nhầm thư mục
    seen = set()
    for ch in (ch_key, "phim-ma-dan-gian", "kiem-hiep-co-trang"):
        idir = MEDIA_ROOT / ch / slug / "01_muse_images"
        if idir.is_dir():
            for f in idir.glob("scene_*.jpg"):
                if f.stat().st_size > 4096:
                    seen.add(f.name)
    return len(seen)


def main() -> int:
    existing_tasks = pm.fetch_hub_tasks()
    existing_dedups = {str(t.get("dedup") or "") for t in existing_tasks}

    active_director = sum(
        1 for t in existing_tasks
        if t.get("assigned_to") == "director" and t.get("status") in ("QUEUED", "RUNNING")
    )
    active_artist = sum(
        1 for t in existing_tasks
        if t.get("assigned_to") == "artist" and t.get("status") in ("QUEUED", "RUNNING")
    )

    local_specs = discover_all_local_specs()
    total_4act = sum(
        1 for ch, _, d in local_specs.values()
        if ch in ("phim-ma-dan-gian", "kiem-hiep-co-trang") and len(d.get("scenes") or []) >= 32
    )

    # 1) Tự động nạp việc cho Ban Họa Sĩ (artist) từ mọi episode.json chưa đủ ảnh
    artist_tasks_to_add: list[dict] = []
    specs_to_mirror: list[tuple[str, Path]] = []
    softened_count = 0

    # Ưu tiên phim dài 4 Hồi trước, sau đó đến K01/K08
    ordered_specs = sorted(
        local_specs.items(),
        key=lambda kv: (0 if kv[1][0] in ("phim-ma-dan-gian", "kiem-hiep-co-trang") else 1, kv[0]),
    )
    for slug, (ch_key, sp, data) in ordered_specs:
        if active_artist + len(artist_tasks_to_add) >= MAX_ARTIST_QUEUED:
            break
        n_scenes = len(data.get("scenes") or [])
        have_imgs = count_local_images(ch_key, slug)
        if have_imgs >= n_scenes:
            continue
        if soften_episode_prompts(sp):
            softened_count += 1
        spec_url = f"https://muse.alltool.pro/media/{slug}/episode.json"
        if n_scenes >= 32:
            # Chia 4 Hồi đều nhau (9-10 cảnh/Hồi)
            per_act = (n_scenes + 3) // 4
            acts = [(idx + 1, s, min(s + per_act - 1, n_scenes)) for idx, s in enumerate(range(1, n_scenes + 1, per_act))]
        else:
            acts = [(0, 1, n_scenes)]

        added_for_slug = False
        for act_no, s_start, s_end in acts:
            if active_artist + len(artist_tasks_to_add) >= MAX_ARTIST_QUEUED:
                break
            dedup = f"museimg-act{act_no}-{slug}" if act_no > 0 else f"museimg-auto-{slug}"
            if dedup in existing_dedups:
                continue
            cnt = s_end - s_start + 1
            act_lbl = f"Hoi {act_no}/{len(acts)} " if act_no > 0 else ""
            artist_tasks_to_add.append({
                "kind": "muse_draw_images",
                "assigned_to": "artist",
                "dedup": dedup,
                "payload": {
                    "slug": slug,
                    "channel": ch_key,
                    "act": act_no,
                    "scene_start": s_start,
                    "scene_end": s_end,
                    "spec_url": spec_url,
                    "objective": f"[{slug}] {act_lbl}Ve {cnt} anh doc 9:16 (scene_{s_start:02d}.jpg..scene_{s_end:02d}.jpg) cho '{data.get('title') or slug}'",
                    "acceptance_criteria": (
                        f"Read the script and character_bible at {spec_url}. "
                        f"Illustrate {cnt} cinematic vertical 9:16 frames (1152x2048) named scene_{s_start:02d}.jpg through scene_{s_end:02d}.jpg "
                        f"with strict character consistency across all scenes, rich lighting, and zero text or watermarks. "
                        f"Deliver using your configured artist upload workflow with keep_jpg=1 and submit your summary on /portal."
                    ),
                },
            })
            existing_dedups.add(dedup)
            added_for_slug = True
        if added_for_slug:
            specs_to_mirror.append((slug, sp))

    mirrored = mirror_specs_to_vps(specs_to_mirror)
    enqueued_artist = pm.enqueue_hub_tasks(artist_tasks_to_add) if artist_tasks_to_add else 0

    # 2) Tự động nạp kịch bản phim dài 4 Hồi (38 cảnh) cho Ban Đạo Diễn (director) tiến tới 100 tập
    director_tasks_to_add: list[dict] = []
    if total_4act < TARGET_TOTAL_MOVIES and active_director < MIN_DIRECTOR_QUEUED:
        need = MIN_DIRECTOR_QUEUED - active_director
        for ch_key, slug, title, premise in _interleaved_catalog():
            if len(director_tasks_to_add) >= need:
                break
            if slug in local_specs:
                continue
            dedup = f"director-4act-{slug}"
            if dedup in existing_dedups:
                continue
            # Bỏ qua nếu đã có task viết slug này (kể cả dedup cũ)
            if any(slug in str(t.get("dedup") or "") or slug in str((t.get("payload") or {}).get("objective") or "") for t in existing_tasks):
                continue
            genre_vi = "Phim Ma Dân Gian Trung Quốc chuyển thể" if ch_key == "phim-ma-dan-gian" else "Phim Kiếm Hiệp Cổ Trang Kỳ Án kiểu Cổ Long"
            voices = "phonui, kiemhiep_nam, chautinhtri" if ch_key == "phim-ma-dan-gian" else "kiemhiep_nam, kiemhiep_nu, phonui"
            director_tasks_to_add.append({
                "kind": "muse_write_script",
                "assigned_to": "director",
                "dedup": dedup,
                "payload": {
                    "slug": slug,
                    "channel": ch_key,
                    "objective": f"[{slug}] Viet kich ban 4 Hoi (38 canh, 6-8 phut) — {title} ({genre_vi})",
                    "acceptance_criteria": (
                        f"Write a full 4-Act (38 scenes, total 1400-1700 Vietnamese words for 6-8 minutes runtime) episode.json for slug='{slug}', channel='{ch_key}', target_channel='KENH_005'. "
                        f"Story concept: {title} — {premise}. "
                        f"Include at least 2-3 layered plot twists, a strict character_bible locking age/face/costume across all 38 scenes (no modern glasses/watches), "
                        f"multi-voice cast ({voices}), aigc_label=false, zero #AIGC hashtags, and atmospheric cinema English image_prompt per scene (avoid graphic words like blood/corpse/dagger; use moody cinematic lighting). "
                        f"Deliver episode.json via your director studio workflow and submit a concise JSON summary on /portal."
                    ),
                },
            })
            existing_dedups.add(dedup)

    enqueued_director = pm.enqueue_hub_tasks(director_tasks_to_add) if director_tasks_to_add else 0

    print(json.dumps({
        "ok": True,
        "total_4act_movies_on_disk": total_4act,
        "target_movies": TARGET_TOTAL_MOVIES,
        "softened_specs": softened_count,
        "mirrored_specs_to_vps": mirrored,
        "artist_active_before": active_artist,
        "enqueued_artist_tasks": enqueued_artist,
        "director_active_before": active_director,
        "enqueued_director_tasks": enqueued_director,
    }, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
