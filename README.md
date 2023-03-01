# Huffman-Encoding-Compression
Project trying to recreate a lossless data compression/decompression algorithm

Had to research and use some well known algorithms such as <br />
 &emsp; -Move-to-front encoding (MTF) <br />
 &emsp; -Burrows Wheeler Transform (BWT) <br />
 &emsp; -Huffman Encoding <br />

To run the file there are a couple flags <br />
&emsp; -b = do not use MTF and BWT<br />
&emsp; -c = compressing file<br />
&emsp; -d = decompressing file<br />
&emsp; -i = input file<br />
&emsp; -o = output file<br />
<br />
When using the b flag with .txt files, it may take a long time as the inverted BWT algorithm is not fully optimized<br />
<br />
EXAMPLES IN BASH:<br />
"python bwt_huffman.py -c -i sample_document.txt -o sample_document.huf"
