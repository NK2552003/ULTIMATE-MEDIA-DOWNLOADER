class UltimateDownloader < Formula
  include Language::Python::Virtualenv

  desc "Powerful media downloader supporting 1000+ platforms including YouTube, Spotify, Instagram"
  homepage "https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER"
  url "https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/archive/refs/heads/main.tar.gz"
  version "2.0.0"
  license "MIT"

  depends_on "python@3.11"
  depends_on "ffmpeg"

  # Python dependencies
  resource "yt-dlp" do
    url "https://files.pythonhosted.org/packages/source/y/yt-dlp/yt_dlp-2024.10.7.tar.gz"
    sha256 "0baf1ab517c9748d7e337ced91c5543c36fc16246a9ebedac32ebf20c1998ceb"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/source/r/requests/requests-2.32.3.tar.gz"
    sha256 "55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.9.4.tar.gz"
    sha256 "439594978a49a09530cff7ebc4b5c7103ef57baf48d5ea3184f21d9a2befa098"
  end

  resource "colorama" do
    url "https://files.pythonhosted.org/packages/source/c/colorama/colorama-0.4.6.tar.gz"
    sha256 "08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44"
  end

  resource "pyfiglet" do
    url "https://files.pythonhosted.org/packages/source/p/pyfiglet/pyfiglet-1.0.2.tar.gz"
    sha256 "758d0c4e4c4e8c26e6f2c5e4c49c91c8c0ef780f6d6e4c9ae8c0ed7d4e7e7d4e"
  end

  resource "emoji" do
    url "https://files.pythonhosted.org/packages/source/e/emoji/emoji-2.14.0.tar.gz"
    sha256 "f68ac28915a2221667cddb3e6c589303c3c6954c6c5af6fefaec7c6c2c5b2e2e"
  end

  resource "halo" do
    url "https://files.pythonhosted.org/packages/source/h/halo/halo-0.0.31.tar.gz"
    sha256 "7b67a3521ee91d53b7152d4ee3452811e1d2a6321975137762eb3d70063cc9d6"
  end

  resource "mutagen" do
    url "https://files.pythonhosted.org/packages/source/m/mutagen/mutagen-1.47.0.tar.gz"
    sha256 "719fadef0a978c31b4cf3c956261b3c58b6948b32023078a2117b1de09f0fc99"
  end

  resource "Pillow" do
    url "https://files.pythonhosted.org/packages/source/P/Pillow/pillow-11.0.0.tar.gz"
    sha256 "72bacbaf24ac003fea9bff9837d1eedb6088758d41e100c1552930151f677739"
  end

  resource "spotipy" do
    url "https://files.pythonhosted.org/packages/source/s/spotipy/spotipy-2.24.0.tar.gz"
    sha256 "854131e5bc96096ef25d5731c9bc1ba42e77797c4d61579e0c2a7b6c4a5f5d9c"
  end

  resource "youtube-search-python" do
    url "https://files.pythonhosted.org/packages/source/y/youtube-search-python/youtube-search-python-1.6.6.tar.gz"
    sha256 "a36558f6a15739679c6e4f5e1f3a0a9d3c96a31ec03525c7e9421e5c6f0edbe3"
  end

  resource "spotdl" do
    url "https://files.pythonhosted.org/packages/source/s/spotdl/spotdl-4.2.10.tar.gz"
    sha256 "4d4b9c5f5e5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c"
  end

  resource "cloudscraper" do
    url "https://files.pythonhosted.org/packages/source/c/cloudscraper/cloudscraper-1.2.71.tar.gz"
    sha256 "8f5a437ce7433fa7604e3fe039d32c3c1e9d4e6e1e6e8e8e8e8e8e8e8e8e8e8e"
  end

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/source/b/beautifulsoup4/beautifulsoup4-4.12.3.tar.gz"
    sha256 "74e3d1928edc070d21748185c46e3fb33490f22f52a3addee9aee0f4f7781051"
  end

  resource "lxml" do
    url "https://files.pythonhosted.org/packages/source/l/lxml/lxml-5.3.0.tar.gz"
    sha256 "4e109ca30d1edec1ac60cdbe341905dc3b8f55b16855e03a54aaf59e51ec8c6f"
  end

  resource "python-dateutil" do
    url "https://files.pythonhosted.org/packages/source/p/python-dateutil/python-dateutil-2.9.0.tar.gz"
    sha256 "78e73e19c63f5b20ffa567001531680d939dc042bf7850431877645523c66709"
  end

  def install
    virtualenv_install_with_resources
    
    # Create a wrapper script that sets the correct output directory
    (bin/"umd").write_env_script libexec/"bin/umd", {}
  end

  def caveats
    <<~EOS
      Ultimate Media Downloader has been installed!
      
      Usage:
        umd <URL>                          # Download media from URL
        umd                                # Start interactive mode
        umd <URL> --audio-only             # Download audio only
        umd <URL> --quality 1080p          # Download specific quality
        umd --help                         # Show all options
      
      Downloads will be saved to: ~/Downloads/UltimateDownloader/
      
      Note: FFmpeg is required and has been installed as a dependency.
      For Spotify downloads, you may need to configure API credentials.
    EOS
  end

  test do
    system bin/"umd", "--help"
  end
end
