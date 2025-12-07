const { ethers } = require("hardhat");

async function main() {
  console.log("=".repeat(80));
  console.log("Hardhat Default Accounts (for local development)");
  console.log("=".repeat(80));
  console.log();
  
  const signers = await ethers.getSigners();
  
  console.log(`Found ${signers.length} accounts\n`);
  
  for (let i = 0; i < Math.min(5, signers.length); i++) {
    const address = await signers[i].getAddress();
    console.log(`Account #${i}:`);
    console.log(`  Address:    ${address}`);
    console.log(`  Private Key: (use the standard Hardhat key below)`);
    console.log();
  }
  
  console.log("=".repeat(80));
  console.log("Standard Hardhat Private Keys");
  console.log("=".repeat(80));
  console.log();
  console.log("Account #0 (RECOMMENDED - Default deployer):");
  console.log("  Address:    0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266");
  console.log("  Private Key: (see Hardhat node output when you run 'npx hardhat node')");
  console.log();
  console.log("Account #1:");
  console.log("  Address:    0x70997970C51812dc3A010C7d01b50e0d17dc79C8");
  console.log("  Private Key: (see Hardhat node output when you run 'npx hardhat node')");
  console.log();
  console.log("Account #2:");
  console.log("  Address:    0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC");
  console.log("  Private Key: (see Hardhat node output when you run 'npx hardhat node')");
  console.log();
  console.log("=".repeat(80));
  console.log("RECOMMENDATION");
  console.log("=".repeat(80));
  console.log();
  console.log("Use Account #0's private key in your backend/.env:");
  console.log("  ETHEREUM_PRIVATE_KEY=<copy from Hardhat node output above>");
  console.log();
  console.log("Why Account #0?");
  console.log("  - It's the default deployer account");
  console.log("  - When you deploy the contract, Account #0 becomes the owner");
  console.log("  - The owner is automatically authorized to issue certificates");
  console.log("  - No additional setup needed!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

