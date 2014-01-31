checkcoverage
=============

A python script to check that the coverage report was run on all .py files
(excluding the tests themselves).

I place a symbolic link to this script in my $HOME/bin directory and add
$HOME/bin to my $PATH environment variable.

  ln -s $(pwd)/checkcoverage.py $HOME/bin/checkcoverage
  export PATH=$PATH:$HOME/bin
