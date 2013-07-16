#!/bin/bash


python_files=$(find . -name "*.py")


function remove_test_files {
	files=$@
	for file in $files
	do
			basename $file | grep "^test_" >/dev/null 2>&1
			if [ $? -eq 0 ]
			then
					continue
			else
					echo "$file"
			fi
	done
}

function clean_pathnames {
	pathnames=$@
	for pathname in $pathnames
	do
		path_length=${#pathname}
		desired_characters=$(($path_length-5))
		newname=${pathname:2:$desired_characters}
		echo $newname
	done
}



filtered_files=$(remove_test_files $python_files)
cleaned_paths=$(clean_pathnames $filtered_files)
coverage_report=$(coverage report)

exit_val=0

for package in $cleaned_paths
do
		if [ "$package" ==  "setup" ]
		then
				continue
		fi
		found_package=0
		for line in $coverage_report
		do
			echo $line | grep "^$package" > /dev/null 2>&1
			if [ $? -eq 0 ]
			then
					found_package=1
					break
			fi
			# replace slashes with periods, in case coverage is using
			# package representation instead of directory representation
			# in its output
			echo $line | sed "s'/'.'g" | grep "^$package" > /dev/null 2>&1
			if [ $? -eq 0 ]
			then
					found_package=1
					break
			fi
		done
		if [ $found_package -eq 0 ]
		then
				echo "\"$package\" module wasn't tested."
				exit_val=1
		fi
done

exit $exit_val
