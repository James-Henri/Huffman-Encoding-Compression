# Huffman-Encoding-Compression
Project trying to recreate a lossless data compression/decompression algorithm

Had to research and use some well known algorithms such as <br />
  -Move-to-front encoding (MTF) <br />
  -Burrows Wheeler Transform (BWT) <br />
  -Huffman Encoding <br />

To run the file there are a couple flags <br />
-b = do not use MTF and BWT
-c = compressing file
-d = decompressing file
-i = image file

When using the b flag with .txt files, it may take a long time as the inverted BWT algorithm is not fully optimized

EXAMPLES IN BASH:
"python bwt_huffman.py -c -i sample_document.txt -o sample_document.huf"
