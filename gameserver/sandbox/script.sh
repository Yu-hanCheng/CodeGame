image=$1
compiler=$2
path=$3
file=$4

cont=$(docker run -it -d "$image" bash)

docker cp $path$file "$cont":/$file
docker exec -i "$cont" sh -c "$compiler $file"
