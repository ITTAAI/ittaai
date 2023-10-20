import Audio from "./Audio.tsx";
import {ThemeProvider} from "@mui/material";
import {appTheme} from "./theme/app.theme.ts";


function App() {

    return (
        <>
            <ThemeProvider theme={appTheme}>
                <Audio/>
            </ThemeProvider>
        </>
    )
}

export default App
