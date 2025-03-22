const bytesFrom = (value) => {
  const jsonStr = JSON.stringify(value);
  return Buffer.from(jsonStr, "utf8");
};

module.exports = { bytesFrom };
