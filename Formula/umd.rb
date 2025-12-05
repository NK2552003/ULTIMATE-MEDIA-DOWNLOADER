class Umd < Formula
  desc "Download media from 1000+ platforms with one command"
  homepage "https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER"
  url "https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/archive/refs/tags/v2.0.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256_HASH"  # Run: curl -sL https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/archive/refs/tags/v2.0.0.tar.gz | shasum -a 256
  license "MIT"
  revision 0

  depends_on "python@3.11"
  depends_on "ffmpeg"
  depends_on "yt-dlp"  # Core dependency

  def install
    # Run the setup.sh script for macOS
    system "bash", "scripts/setup.sh"
  end

  test do
    system "#{bin}/umd", "--version"
  end
end
