# /usr/bin/sed
# run script with: sed -f test.sed in_file > out_file

s/\(^d{1,3},\s?d{1,3},\s?and\s?d{1,3}\.\)/@@OBJECT@@\n\1/g
s/\(^d{1,3}\s?and\s?d{1,3}\.\)/@@OBJECT@@\n\1/g
s/\(^d{1,3}\.\)/@@OBJECT@@\n\1/g