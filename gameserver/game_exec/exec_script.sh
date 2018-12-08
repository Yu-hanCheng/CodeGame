image=$1
compiler=$2
path=$3
file=$4
link=$5
log_id=$6
userId=$7


echo expr $userId - "0"
echo "$(($userId + 0))"

if [ "$link" -eq "0" ]; then
    cont=$(docker run --name "$log_id$file" --net="codegame" -ti -d $image bash)
    echo path: $path$file
    docker cp $path$file "$cont":/$file
    docker exec -i "$cont" sh -c "cd /;$compiler $file $log_id"
else
    cont=$(docker run --name "$file" --net="codegame" -ti -d "$image" bash)
    docker cp $path$file "$cont":/$file
    
    docker exec -i "$cont" sh -c "cd /;$compiler $file $link "$(($userId + 0))""

fi

