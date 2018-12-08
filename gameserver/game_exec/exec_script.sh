image=$1
compiler=$2
path=$3
file=$4
link=$5
log_id=$6

if [ "$link" -eq "0" ]; then
	cont=$(docker run --name "$log_id$file" --net="codegame" -ti -d 41f2086aefd8 bash)
    echo gamemain"$compiler $file"
    docker cp $path$file "$cont":/$file
    docker exec -i "$cont" sh -c "$compiler $file $log_id"
else
    cont=$(docker run --name "$file" --net="codegame" -ti -d "$image" bash)
    echo the link"$link"
    docker cp $path$file "$cont":/$file
    docker exec -i "$cont" sh -c "$compiler $file $link"
fi

