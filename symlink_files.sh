#!/bin/zsh

for i in `ls`; do

  # FIXME: this compare line doesn't work
  if [[ ($i == *~ | $i == "README.rst" | $i == "scripts" | $i == *.txt | $i == ".git" | $i == "trac-plugins" | $i == "symlink_files.sh" ) ]]
  then
      echo "Excluding ${i}"
  else
      echo mv -f $HOME/$i $HOME/$i.dotfiles # remove/backup duplicates
      cd $HOME
      echo ln -s `pwd`/$i . # copy new files in
  fi
done

cd -

echo "Symlinking successful."
