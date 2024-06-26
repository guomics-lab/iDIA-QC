
<p align="center" style="margin-bottom: 0px !important;">
  <img src="https://github.com/guomics-lab/iDIA-QC/blob/main/resource/logo/iDIAQC-logo.png" width="100" height="100">
</p>
<h1 align="center" style="margin-top: -10px; font-size: 20px">iDIA-QC</h1>

iDIA-QC is a Python Graphical User Interface (GUI) for a suite of analytical tools enabling comprehensive evaluation and analysis of the quality of mass spectrometry-based DIA files. The software incorporates the protein qualitative and quantitative algorithms from DIA-NN and uses msConvert for file conversion to extracted precursor ion chromatogram (PIC). Based on 15 metrics extracted from the DIA files, which describe the characteristics of the raw files from timsTOF serial instruments, TripleTOF instruments, and Orbitrap serial instruments, we utilize machine learning models to predict the quality of the DIA files. The outputs of iDIA-QC in a longitudinal summary, visually display the quality of the DIA files. Additionally, it promptly shares the prediction results and visualization with administrators via email and WeChat.

iDIA-QC is built on the following principles:
Ease of use: high degree of automation. With just a few mouse clicks, one can easily grasp the data generated by fully automated monitoring instruments without the need for expertise in mass spectrometry.
Clear Output Results: Machine learning outputs feature results and status information of the original file, along with potential instrument issues.
Scalability and speed: Analysis time per file is under 5 minutes.

### Getting Started
DIA mass spectrometry data can be analyzed in two ways: Automatic monitoring mode and manually inspection mode. Click Raw (in the Input pane), select your raw mass spectrometry data files. This software supports the .raw, .d, and .wiff raw data formats. Choose the type of instrument that generated the file. Assign an instrument ID to the corresponding instrument for this file. Choose the notification method for the "output", such as email or WeChat with token ID.
Note: To obtain the token ID, follow the WeChat public account **"pushplus推送加"**. The official website is www.pushplus.plus.

Enter the output directory information for the file path. Click "Run" to start the analysis.

### Output
The Output pane allows to specify where the output should be saved. There are two types of output files produced by iDIA-QC: html report, matrices (easy-to-use even without statistical software such as R/Python). The html report can find information on each of these.
