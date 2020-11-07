# 2020/11/08 - Fixing timeout issue and adding error catching
* Can catch any error as an event.
* Fix timeout of boto3 when calling lambda function.

# 2020/11/07 - Adding autobuider to lambda functions
* Added `autobuilder` to lambda functions.
* Added environment variable `S3_BUCKET` with the name of the S3 bucket where files will be stored.
* Added event process to `build_adgroups`.
* Correct text explaining column names of the `build_adgroups` template.
* Removing unneeded dependencies from `./requirements.txt` to simplify built.