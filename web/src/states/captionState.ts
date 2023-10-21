import {atom} from "recoil";

interface CaptionState {
    value: string
}

export const captionState = atom<CaptionState>({
    key: 'captionState',
    default: {
        value: ''
    }
})