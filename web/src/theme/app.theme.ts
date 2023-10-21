import {createTheme} from "@mui/material";

export const appTheme = createTheme({
    palette: {
        primary: {
            main: "#cee5fa",
        }
    },
    components: {
        MuiButton: {
            defaultProps: {
                disableElevation: true,
            },
            styleOverrides: {
                containedPrimary: {
                    color: "#000",
                },
                root: {
                    textTransform: "none",
                    borderRadius: 10,
                }
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    "&[href]": {
                        textDecorationLine: "none",
                    },
                    borderRadius: 10,
                },
                outlined: {
                    display: "block",
                    "a&, button&": {
                        "&:hover": {
                            boxShadow: "1px 1px 20px 0 rgb(90 105 120 / 20%)",
                        },
                    },
                },
                elevation: {
                    boxShadow: '0 0 0 0 rgb(0 0 0 / 20%), 0 0 0 0 rgb(0 0 0 / 14%), 0 0 0 0 rgb(0 0 0 / 12%);'
                }
            },
        },
    }
})