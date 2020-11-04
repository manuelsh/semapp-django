# Funciton to upload the code in the builders lambda function
zip code *.py
aws lambda update-function-code --function-name builders --zip-file fileb://code.zip --publish
