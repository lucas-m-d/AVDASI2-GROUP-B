export default async function testFlapIndicator(
    desired: number | undefined, 
    current: [number?, number?]
  ): Promise<[number, number] | undefined> {
  
    const update = 250;
  
    // Helper function to create a delay
    const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
  
    // Base case: if inputs are invalid, return undefined
    if (desired === undefined || current[0] === undefined || current[1] === undefined) {
      console.log(desired, current);
      return;
    }
  
    // If the current flap matches the desired flap, return the current value
    if (desired === current[0]) {
      return current as [number, number];
    }
  
    // Recursive step: adjust the flap by 1 step toward the desired position
    if (desired < current[0]) {
      await delay(update);
      return testFlapIndicator(desired, current.map(x => x! - 1) as [number, number]);
    }
  
    if (desired > current[0]) {
      await delay(update);
      return testFlapIndicator(desired, current.map(x => x! + 1) as [number, number]);
    }
  
    return;
  }