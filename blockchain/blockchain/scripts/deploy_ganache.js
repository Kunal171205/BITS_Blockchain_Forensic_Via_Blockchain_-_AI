import hre from "hardhat";

async function main() {
  console.log("Deploying DocumentRegistry...");

  const registry = await hre.ethers.deployContract("DocumentRegistry");

  await registry.waitForDeployment();

  console.log(`DocumentRegistry deployed to: ${registry.target}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
