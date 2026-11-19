# BTL TTNT – Đề tài 12: Tác tử điều hướng trong mê cung (quan sát một phần)

Project chạy bằng Python 3 thuần, không cần cài thư viện.

## Cấu trúc
```
BTL_TTNT_DeTai12/
  shared_api.py        hằng số và hướng đi dùng chung (UNKNOWN/FREE/WALL, DIRECTIONS)
  maze_env.py          sinh mê cung theo MSSV + môi trường quan sát một phần + run_episode
  run_experiments.py   chạy mọi thuật toán trên cùng bộ mê cung, in bảng, lưu ket_qua.csv
  trace_run.py         in nhật ký từng bước của một thuật toán trên một mê cung
  mssv_list.txt        danh sách MSSV (mỗi MSSV = một mê cung)
  algorithms/          mỗi thuật toán một file, có hàm choose_action(...)
    online_dfs.py      (TV1)
    lrta_star.py       (TV2)
    node_counting.py   (TV3)
    edge_counting.py   (TV4)
    min_lrta_star.py   (TV5)
  export_demo.py       tạo trang demo hoạt ảnh của cả 5 thuật toán từ mssv_list.txt
  demo/                demo_thuat_toan.html: trang demo (mở bằng trình duyệt)
```

## Chạy so sánh các thuật toán
```
python run_experiments.py                       # đọc mssv_list.txt
python run_experiments.py --mssv 072206011102 --mssv <MSSV khác> --mssv <MSSV khác>
```
In bảng từng mê cung và bảng tổng hợp, lưu `ket_qua.csv`. Mọi thuật toán chạy trên cùng bộ
mê cung. Đầu kết quả có phần tự kiểm tra API: [OK] / [CẢNH BÁO] / [THIẾU].
Đề yêu cầu ít nhất 3 mê cung, nên cần ít nhất 3 MSSV.

## Xem nhật ký từng bước (cho mục "Ví dụ chạy từng bước")
```
python trace_run.py --algo lrta_star --demo-trap            # mê cung nhỏ có bẫy chữ U
python trace_run.py --algo lrta_star --mssv 072206011102 --max-lines 15
python trace_run.py --algo node_counting --demo-trap
```
`--algo` nhận tên bất kỳ file trong `algorithms/`. Cột Ghi chú chỉ hiện "H cũ -> H mới" cho LRTA*.
Số bước do vòng lặp của môi trường đếm: mỗi lần gọi choose_action robot đi đúng một ô.

## Trang demo
Mở `demo/demo_thuat_toan.html` bằng trình duyệt (không cần mạng). Chọn một trong 3 mê cung sinh từ MSSV,
rồi xem cả 5 thuật toán chạy cùng lúc hoặc chọn một thuật toán (có thể hiện giá trị H của LRTA*).
Nút Chạy, Tạm dừng, Bước tiếp, Lùi 1, thanh kéo bước và thanh tốc độ. Bảng bên dưới là số bước từng thuật toán.
Đường đi trong trang là kết quả chạy thật của code trong `algorithms/`. Khi sửa thuật toán hoặc đổi MSSV,
chạy lại để cập nhật trang demo:
```
python export_demo.py
```

## Quy ước sinh mê cung từ MSSV (nhóm cần thống nhất và ghi vào báo cáo)
Coi MSSV là số nguyên N (bỏ số 0 đầu). Seed = N.
- Số ô-đường theo hàng = 6 + N mod 7; theo cột = 6 + (N // 7) mod 7
- Lưới thật = 2n + 1 mỗi chiều (13 đến 25)
- Start = (1,1), goal = (hàng-2, cột-2); luôn có đường đi
- Tạo bằng DFS, rồi phá ngẫu nhiên 8% tường trong để có vòng lặp

Ví dụ MSSV 072206011102: lưới 15 x 17, giới hạn 2550 bước, đường ngắn nhất 50 bước.
Đề không định nghĩa "kích thước theo MSSV" nên cần hỏi thầy xác nhận cách này.

## Thêm hoặc thay thuật toán
Đặt file vào `algorithms/` với đúng tên ở trên, hàm `choose_action(current, goal, known_map, memory)`
trả về `(action, memory)`. Thuật toán mới: thêm một dòng vào `ALGORITHMS` trong `run_experiments.py`.

## Điểm cần lưu ý (đã phát hiện khi chạy thử)
- `edge_counting.py`: khi không có ô kề FREE, hàm trả về hướng UP thay vì `None` như API chung.
  Với mê cung sinh ở đây không xảy ra, nhưng nên sửa cho đúng.
- `online_dfs.py`: lưu tập `visited` nhưng không dùng khi chọn hướng; chỉ nhớ hướng đã thử tại từng ô.
- `min_lrta_star.py` mặc định khởi tạo V = 0 đúng bài báo gốc nên đi nhiều bước hơn LRTA*. Chế độ
  "manhattan" là mở rộng của nhóm và không luôn ít bước hơn (xem tiểu luận, Bảng 5.5).
