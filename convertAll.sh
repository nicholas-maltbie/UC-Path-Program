#Convert all pdf files in this directory to images
#
#Convert command from here - https://glenbambrick.com/2017/01/10/pdf-to-jpg-conversion-with-python-for-windows/
#

for file in *.pdf;
do
    echo Converting $file
    convert $file ${file%.*}.jpg;
done
echo done
