#! /bin/bash
echo 'Combining Seed_List_enwiki & Grown_Seed_list_enwiki'
echo 'Cleaning output file to only contain column one'
sed -E -e 's/(\w+).*/\1/g' Seed_List_enwiki_*.txt > Seed_List_And_Grown.lst
sed -E -e 's/(\w+).*/\1/g' Grown_Seed_List_enwiki_*.txt >> Seed_List_And_Grown.lst
echo 'Complete. File Seed_List_And_Grown.lst generated'
