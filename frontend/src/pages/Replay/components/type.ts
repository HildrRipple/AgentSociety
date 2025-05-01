export interface AgentProfile {
    id: string;
    name: string;
    profile?: { [key: string]: string | number };
}

export interface AgentStatus {
    id: string;
    day: number;
    t: number;
    lng: number;
    lat: number;
    parent_id: number;
    action: string;
    status: { [key: string]: string | number };
}

export interface AgentDialog {
    id: string;
    day: number;
    t: number;
    type: 0 | 1 | 2;
    speaker: string;
    content: string;
}

export interface AgentSurvey {
    id: string;
    day: number;
    t: number;
    survey_id: string;
    result: { [key: string]: string | number };
}

export interface Agent extends AgentProfile, AgentStatus { }

export interface Time {
    day: number;
    t: number;
}

export interface LngLat {
    lng: number;
    lat: number;
}

export interface ApiMLflowMetric {
    key: string;
    value: number;
    step: number;
    is_nan: boolean;
}
