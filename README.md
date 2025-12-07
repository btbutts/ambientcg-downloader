# ambientCG Downloader

### Credit to the original creator:  [Álvaro González _@alvarognnzz_](https://github.com/alvarognnzz)

## Download all the CC0 textures from the official ambientcg.com website easily.

<p align="center">
  <img src="https://github.com/user-attachments/assets/0efce479-5cbe-4ed1-9805-818c18b6a151" />
</p>

## This cloned repo features several improvements:
1. Bug Fix

   As of 06DEC2025, the original version has an issue where if you follow the poetry initiated version of this tool, and conifgure the python script's config.yaml file to download 2K materials, it will download both 2K and 12K files, resulting in significant donwload sizes and long delays. This is patched.

2. Improvement

   The original version can only download one file at a time, Again, this results in significantly long delays to download the entire asset library as there are over 2K individual assets by my count [06DEC2025]. My patched script, _main.py_, will download a minimum of 2 material files at a time, and a maximum of 8, determined by the following sequential equations:
   * (Machine_CPU_Cores × 1.25 = _𝐗<sub>Rounded\_Up\_To\_Integer</sub>_)
   * If _𝐗_ is not ÷ by 2, then _𝐗_ = _𝐗_ + 1
   * If _𝐗_ < 2, then concurrent download threads shall be 2 threads.
   * If _𝐗_ > 8, then concurrent download threads shall be 8 threads.
   * If 2 < _𝐗_ < 8, then concurrent download threads shall be _𝐗_ threads.

3. Messaging and Error Reporting:

   Along with downloading multiple files simultaneously, the script will better display current download operations, whether it is downloading a file or skipping a file (if it already exists). It will also display throughput information, time started and ended.
   For example:
   ```
   [DOWNLOADING] /Volumes/Multimedia/Blender/AmbientCG_Materials/3DBread004_LQ-2K-PNG.zip -> 0.4 MB / 30.8 MB | Speed: 615.04 KB/s
   [SKIPPING] /Volumes/Multimedia/Blender/AmbientCG_Materials/Foliage003_2K-PNG.zip already exists.
   [DOWNLOADING] /Volumes/Multimedia/Blender/AmbientCG_Materials/3DBread004_HQ-2K-PNG.zip -> 0.8 MB / 43.2 MB | Speed: 1357.35 KB/s
   ```

4. Read Me is updated to include easier to follow instructions for users unfamiliar with python. This democratizes the script to be suitable for less technically oriented users.

## Download the entire ambientCG texture library
This repository was created to simplify a repetitive process: downloading textures from ambientCG, extracting them, and manually removing unused images.

With this automation, all textures are pre-downloaded to your computer. Once you find the texture you need on the ambientCG website, you can quickly locate it locally without additional steps.

## Installation  

You can set up the project in two ways: using **Poetry** or a traditional setup with `requirements.txt`. Choose the poetry if you want to avoid dependencies issues.  

### Option 1: Using Poetry  
1. Ensure you have [Poetry](https://python-poetry.org/) installed.  
   ```bash
   pip install poetry
   ```
2. Clone the repository:  
   ```bash
   git clone https://github.com/alvarognnzz/ambientcg-downloader
   cd ambientcg-downloader
   ```
3. Install dependencies:  
   ```bash
   poetry install
   ```
4. Run the script:  
   ```bash
   poetry run python main.py
   ```

### Option 2: Without Poetry
1. Clone the repository:  
   ```bash
   git clone https://github.com/alvarognnzz/ambientcg-downloader
   cd ambientcg-downloader
   ```
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:  
   ```bash
   python script.py
   ```

Both methods will set up the environment for running the project. If you're new to dependency management, the second option (`requirements.txt`) is more straightforward.

## Setting up the script  

To configure the script, use the `config.yaml` file. Here's an example configuration:  

```yaml
resolution: "1K"                  # (1K, 2K, 4K, 8K)
file_type: "JPG"                  # (JPG/PNG)
downloads_folder: "downloads"
unzip: 
  enabled: true                   # (true/false)
  folder: "unzipped"
keep_files:                       # Files marked as false will be deleted
  color: true
  roughness: true
  normal_gl: true
  normal_dx: true
  metalness: true
  opacity: true
  ambient_occlusion: true
  displacement: false
  cover: false
```

### How to use it  

1. **Adjust the settings**  
   - Open the `config.yaml` file in a text editor.  
   - Set the `resolution` to the desired quality (e.g., "1K", "2K").  
   - Choose the `file_type` (either "JPG" or "PNG").  
   - Specify the folder for downloaded textures under `downloads_folder`.  

2. **Configure unzipping**  
   - If you want the textures to be automatically extracted, set `enabled` to `true`.  
   - Define the folder for unzipped files under `folder`.  

3. **Manage file types**  
   - In the `keep_files` section, mark the file types you want to keep as `true`.  
   - Any file type set to `false` will be deleted after extraction.  

4. **Run the script**  
   - Save your changes to the `config.yaml` file.  
   - Execute the script, and it will follow the configuration to download, unzip, and manage the textures automatically.

> [!WARNING]  
> The ambientCG texture library is quite large, with a size of up to 10GB at 1K resolution.  
> If you select a higher resolution (e.g., 2K or 4K), the download process may take several hours depending on your internet speed and system performance.

