const Pool = require("threads").Pool;

const pool = new Pool();
pool.on("done", (job, message) => console.log("Job done:", message));
pool.on("error", (job, error) => console.error("Job errored:", job));
pool.on("finished", () => {
  console.log("Everything done, shutting down the thread pool.");
  pool.killAll();
});

const compute = (str, done) => {
  done(str + str);
};

for (let i = 0; i < 100; i++) {
  pool.run(compute).send(i.toString());
}
