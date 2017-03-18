// For use with nodejs to quickly check the size of generated lists
// The sizes checked are to ensure the target zim size is correct.

var fs = require('fs');
var readline = require('readline')

var seedList = readline.createInterface({
  input: fs.createReadStream('Seed_List_enwiki_2016-06.txt')
});

seedList.total = 0;
seedList.on('line', function(line) {
  line = parseInt(line.split(/\s+/)[2]);
  if (!isNaN(line)) {
    seedList.total += line;
  }
})
seedList.on('close', () => {
  console.log('Seed List:', seedList.total);
})

// ----------------------------- //
// Duplicate for Grown Seed List //
// ----------------------------- //

var grownSeedList = readline.createInterface({
  input: fs.createReadStream('Grown_Seed_List_enwiki_2016-06.txt')
});

grownSeedList.total = 0;
grownSeedList.on('line', function(line) {
  line = parseInt(line.split(/\s+/)[2]);
  if (!isNaN(line)) {
    grownSeedList.total += line;
  }
})

grownSeedList.on('close', function() {
  console.log('Grown Seed List: ', grownSeedList.total);
})