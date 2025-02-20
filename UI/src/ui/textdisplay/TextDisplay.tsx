
import { Typography } from "@mui/material";

interface TextDisplayProps {
    textArray: Array<string>;
}



export default function TextDisplay ({textArray}:TextDisplayProps) {

    
    return (
        <div style={{
            paddingTop: "1rem"
        }}>
            <Typography variant="h6" align="center">
            Log
            </Typography>
           
        
        <div style={{
            width:"auto",
            height:"500px",
            border: "2px",
            overflowY: "scroll",
            wordBreak: "break-all",
            backgroundColor: "#e0e0e0",
            scrollbarWidth: "thin"
        }}>
            
            
            {
                textArray && textArray.map((text) => (
                    <Typography variant="body1" style={{
                        padding:"2px",
                        paddingLeft:"5px"
                    }}>{text}</Typography>
                ))
            }

        </div>
        </div>
    )
}

const testingText = [
    "The apple is red and juicyaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa asdfa sd.", "Bananas are a great source of potassium.", 
    "Cherries taste best in the summer.", "Dates are a sweet and chewy fruit.", 
    "Elderberries are used to make syrups.", "Figs are delicious when dried.", 
    "Grapes can be made into wine.", "Honeydew melons are refreshing on hot days.", 
    "Kiwis have a fuzzy skin and green flesh.", "Lemons add a tangy flavor to dishes.", 
    "Mangoes are popular in tropical regions.", "Nectarines are similar to peaches.", 
    "Oranges provide a lot of vitamin C.", "Papayas have a soft and sweet taste.", 
    "Quinces are often made into jams.", "Raspberries are both sweet and tart.", 
    "Strawberries are perfect for desserts.", "Tangerines are small and easy to peel.", 
    "Ugli fruit is a hybrid citrus variety.", "Vanilla beans are used for flavoring.", 
    "Watermelons are mostly made of water.", "Xigua is a type of Chinese watermelon.", 
    "Yellow passion fruit is very aromatic.", "Zucchini is actually a type of fruit.", 
    "Apricots are small, orange, and sweet.", "Blackberries grow on thorny bushes.", 
    "Cantaloupes have a netted rind.", "Dragon fruit has a unique appearance.", 
    "Eggplants are used in many savory dishes.", "Feijoas have a fragrant flavor.", 
    "Gooseberries can be green or red.", "Hackberries are edible but not common.", 
    "Imbe is a small African fruit.", "Jabuticaba fruit grows directly on the trunk.", 
    "Kumquats can be eaten whole.", "Limes are essential for making mojitos.", 
    "Mulberries can stain your fingers.", "Nashi pears are crisp and juicy.", 
    "Olives are often preserved in brine.", "Plantains must be cooked before eating.", 
    "Quenepas are also known as Spanish limes.", "Red currants are used in jellies.", 
    "Salak is also called snake fruit.", "Tamarillos have a tangy taste.", 
    "Uvaia is a rare South American fruit.", "Voavanga is known as the Spanish tamarind.", 
    "White currants are less tart than red ones.", "Ximenia is a wild African fruit.", 
    "Yangmei is a juicy Chinese fruit.", "Ziziphus is also called jujube."
  ];