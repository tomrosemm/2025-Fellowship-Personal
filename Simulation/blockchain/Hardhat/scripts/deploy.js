async function main() {
    const Auth = await ethers.getContractFactory("Authentication");
    const auth = await Auth.deploy();
    await auth.deployed();
    console.log("Authentication deployed to:", auth.address);
}
main();