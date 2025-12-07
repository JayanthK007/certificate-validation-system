const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying CertificateVerifier contract...");
  console.log("Network:", hre.network.name);
  
  if (hre.network.name === "localhost") {
    console.log("⚠️  Connecting to persistent Hardhat node at http://127.0.0.1:8545");
    console.log("   Make sure the node is running: npx hardhat node");
  }
  
  const CertificateVerifier = await hre.ethers.getContractFactory("CertificateVerifier");
  
  const certificateVerifier = await CertificateVerifier.deploy();
  
  await certificateVerifier.waitForDeployment();
  
  const address = await certificateVerifier.getAddress();
  console.log("✅ CertificateVerifier deployed to:", address);
  console.log("Chain ID:", (await hre.ethers.provider.getNetwork()).chainId);
  
  const deploymentInfo = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    contractAddress: address,
    deployer: (await hre.ethers.provider.getSigner()).address,
    timestamp: new Date().toISOString(),
    blockNumber: (await hre.ethers.provider.getBlockNumber()).toString(),
  };
  
  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }
  
  const deploymentFile = path.join(
    deploymentsDir,
    `deployment-${hre.network.name}.json`
  );
  fs.writeFileSync(
    deploymentFile,
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log("\n📝 Deployment info saved to:", deploymentFile);
  console.log("\nNext steps:");
  console.log("1. Update backend/.env with CONTRACT_ADDRESS=" + address);
  console.log("2. Update backend/.env with NETWORK=" + hre.network.name);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

