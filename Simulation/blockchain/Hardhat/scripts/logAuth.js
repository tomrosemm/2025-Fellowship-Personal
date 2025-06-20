async function main() {
    const [deployer] = await ethers.getSigners();
    const auth = await ethers.getContractAt("Authentication", "<DEPLOYED_ADDRESS>");
    await auth.logAuth("0x...", 1234567890, true);
}
main();