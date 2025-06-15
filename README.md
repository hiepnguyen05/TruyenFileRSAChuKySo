<div class="project-intro" style="font-family: Arial, sans-serif; max-width: 800px; margin: auto; line-height: 1.6;">
  <h2 style="text-align: center; color: #2c3e50;">Giới thiệu dự án TruyenFileRSAChuKySo</h2>
  
  <p>
    <strong>TruyenFileRSAChuKySo</strong> là một ứng dụng web được phát triển bằng <em>Flask</em>, cung cấp giải pháp truyền file bảo mật qua mạng với <strong>mã hóa RSA</strong> và <strong>chữ ký số</strong> để đảm bảo tính toàn vẹn và xác thực nguồn gốc. Ứng dụng cho phép người gửi tải lên file cùng file chữ ký số (`.sig`) tự tạo, mã hóa file bằng khóa công khai của người nhận, và người nhận giải mã bằng khóa bí mật, đồng thời xác minh chữ ký bằng khóa công khai của người gửi. Giao diện được thiết kế hiện đại với <em>Tailwind CSS</em>.
  </p>

  <p>Những chức năng nổi bật của ứng dụng:</p>
  <ul>
    <li><strong>Đăng nhập và quản lý người dùng:</strong> Hệ thống hỗ trợ đăng nhập với tài khoản mặc định (Hiệp, Hoàng, Huy) và tạo tài khoản mới, đảm bảo phân biệt truy cập.</li>
    <li><strong>Mã hóa RSA:</strong> File được mã hóa bằng khóa công khai của người nhận (OAEP padding), đảm bảo chỉ người nhận có khóa bí mật mới giải mã được.</li>
    <li><strong>Chữ ký số:</strong> Người gửi tải lên chữ ký số (`.sig`) tự tạo bằng khóa bí mật (PSS padding, SHA256), đính kèm file để xác minh tính toàn vẹn và nguồn gốc.</li>
    <li><strong>Xác minh chữ ký:</strong> Hệ thống tự động kiểm tra chữ ký khi gửi và nhận, hiển thị trạng thái "Hợp lệ"/"Không hợp lệ" cùng chữ ký dạng base64.</li>
    <li><strong>Quản lý khóa:</strong> Người dùng xem khóa công khai và bí mật trong giao diện, hỗ trợ tạo chữ ký và xác minh thủ công.</li>
    <li><strong>Tải file an toàn:</strong> Người nhận tải file mã hóa (`.enc`), chữ ký (`.sig`), hoặc file giải mã đã được xác minh tính toàn vẹn.</li>
    <li><strong>Giao diện thân thiện:</strong> Sử dụng Tailwind CSS, thiết kế responsive, với thông báo rõ ràng (thành công: xanh, lỗi: đỏ).</li>
  </ul>

  <div style="display: flex; justify-content: space-around; margin-top: 30px;">
    <div style="flex: 1; margin-right: 10px; text-align: center;">
      <h3>Giao diện đăng nhập</h3>
      <img src="https://github.com/hiepnguyen05/TruyenFileRSAChuKySo/blob/main/Login.png?raw=true" alt="Ảnh màn hình đăng nhập" style="max-width: 100%; border: 1px solid #ccc; border-radius: 8px;">
      <p>Người dùng đăng nhập an toàn với danh sách tài khoản được hiển thị sẵn.</p>
    </div>
    <div style="flex: 1; margin-left: 10px; text-align: center;">
      <h3>Giao diện truyền file</h3>
      <img src="https://github.com/hiepnguyen05/TruyenFileRSAChuKySo/blob/main/TrangChu.png?raw=true" alt="Ảnh giao diện truyền file" style="max-width: 100%; border: 1px solid #ccc; border-radius: 8px;">
      <p>Giao diện cho phép chọn người nhận, tải file và chữ ký, xem file nhận với trạng thái chữ ký và chữ ký base64.</p>
    </div>
  </div>

  <p style="margin-top: 30px;">
    Dự án phù hợp với những ai muốn tìm hiểu về mã hóa bất đối xứng, chữ ký số, và phát triển ứng dụng web bảo mật với Flask, cung cấp nền tảng thực hành các khái niệm bảo mật hiện đại.
  </p>
</div>
