# Video-Scraper

Video-Scraper is a Python-based GUI application designed to download video files from `.i3u8` playlists and optionally merge them into a single `.mkv` file. It provides a user-friendly interface for managing download tasks and supports multithreaded downloading for improved performance.

## Features

- **Multithreaded Downloading**: Uses a thread pool to download multiple `.ts` files concurrently.
- **Customizable Thread Count**: Allows users to specify the number of threads for downloading.
- **File Merging**: Automatically merges downloaded `.ts` files into a single `.mkv` file.
- **Error Handling**: Logs download failures and retries failed downloads up to a specified number of attempts.
- **Modern GUI**: Built with PyQt6, featuring a dark-themed interface for ease of use.
- **Input Validation**: Ensures that user inputs are correctly formatted before starting the download process.

## Requirements

To run this application, you need the following:

- Python 3.9 or later
- Required Python packages:
  - `PyQt6`
  - `requests`

You can install the required packages using pip:

```bash
pip install PyQt6 requests
```

## How to Use

1. **Launch the Application**: 
    - Run the `Video-Scraper_src.pyw` file to open the GUI.
2. **Input the Link URL**:
   - Enter the base URL of the `.ts` in the "Link URL" field.
   - Example: `https://www.example.com/ts/`
3. **Paste the `.i3u8` Content**:
   - Copy and paste the content of the `.i3u8` file into the "`.i3u8` Content" field.
   - Ensure it contains `.ts` file references (e.g., `00000.ts`, `00001.ts`).
4. **Set the Thread Count**:
   - Specify the number of threads for downloading in the "ThreadPool Executor" field.
   - Default: `10`
5. **Choose the Save Format**:
   - Select either `.mkv` or `.ts` as the output format.
6. **Start the Process**:
   - Click the "Start" button to begin downloading and merging files.
7. **Monitor Progress**:
   - View the download progress in the progress bar and logs in the log output area.

## Application Workflow

1. **Input Validation**:
   - Validates the URL, `.i3u8` content, and thread count.
2. **Download Process**:
   - Downloads `.ts` files concurrently using a thread pool.
   - Logs progress and errors during the download.
3. **File Merging** (if `.mkv` is selected):
   - Merges all downloaded `.ts` files into a single `.mkv` file.
   - Deletes the original `.ts` files after merging.

## Example

### Input Example

- **Link URL**: 
  ```
  https://www.example.com/
  ```
- **`.i3u8` Content**:
  ```
  00000.ts
  00001.ts
  00002.ts
  ```

### Output

- Downloaded `.ts` files saved in a timestamped directory (e.g., `ts-mkv_1691234567`).
- Merged `.mkv` file (e.g., `mkv_1691234567.mkv`).

## Error Handling

- Logs errors for failed downloads and retries up to the specified number of attempts.
- Displays a message if any files fail to download after all retries.

## Closing the Application

When attempting to close the application, a confirmation dialog will appear to prevent accidental closure.

## License

\# None

## Acknowledgments

- Built with [PyQt6](https://riverbankcomputing.com/software/pyqt/intro) for the GUI.
- Uses [requests](https://docs.python-requests.org/en/latest/) for HTTP requests.

### \# The `Markdown` file was created by `ChatGPT-4o`
