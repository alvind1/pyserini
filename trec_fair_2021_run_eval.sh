#arg 1 should be eval-folder
#args 2 ... should be run files

eval_folder=$1
echo $eval_folder
shift
cp "$@" .
