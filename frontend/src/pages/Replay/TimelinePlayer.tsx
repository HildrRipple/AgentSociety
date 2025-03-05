import React, { useContext, useEffect, useRef, useState } from 'react';
import { Button, Flex, Select, Slider, SliderSingleProps, Space, Tooltip } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, FastForwardOutlined, FastBackwardOutlined, UpOutlined, ReloadOutlined, ToolOutlined } from '@ant-design/icons';
import { parseT } from '../../components/util';
import { observer } from 'mobx-react-lite';
import { StoreContext } from './store';
import { experimentStatusMap } from '../../components/type';
import FlickeringDot from '../../components/FlickeringDot';

const TimelinePlayer = observer(({ initialInterval }: {
    initialInterval: number,
}) => {
    const store = useContext(StoreContext)

    const [isLiveMode, setIsLiveMode] = useState<boolean>(false);

    const [sliderChanging, setSliderChanging] = useState(false);

    const [currentIndex, setCurrentIndex] = useState<number>(0);
    const [isPlaying, setIsPlaying] = useState<boolean>(false);
    const [playInterval, setPlayInterval] = useState<number>(initialInterval);
    const intervalRef = useRef<any>();

    const currentTimeline = store.timeline[currentIndex] || { day: 0, t: 0 };

    const nextIndex = () => {
        if (isLiveMode) {
            store.refresh().then(() => {
                setCurrentIndex(store.timeline.length - 1);
            });
        } else {
            if (currentIndex < store.timeline.length - 1) {
                setCurrentIndex(currentIndex + 1);
            } else {
                clearInterval(intervalRef.current);
                setIsPlaying(false);
            }
        }
    };

    const prevIndex = () => {
        if (currentIndex > 0) {
            setCurrentIndex(currentIndex - 1);
        }
    };

    useEffect(() => {
        if (isPlaying) {
            intervalRef.current = setInterval(nextIndex, playInterval);
        } else {
            clearInterval(intervalRef.current);
        }
        return () => clearInterval(intervalRef.current);
    }, [isPlaying, playInterval, currentIndex, isLiveMode]);

    const handleSliderChange = (value) => {
        setSliderChanging(true);
        setCurrentIndex(value);
        setIsPlaying(false);
    };

    const handleSliderChangeEnd = (value) => {
        setSliderChanging(false);
        setCurrentIndex(value);
    }

    const formatter: NonNullable<SliderSingleProps['tooltip']>['formatter'] = (value) => {
        if (value === undefined || store.timeline[value] === undefined) {
            return '';
        }
        const t = store.timeline[value];
        return `Day ${t.day} ${parseT(t.t)}`;
    }

    useEffect(() => {
        console.log('currentTimeline', `Day ${currentTimeline.day} ${parseT(currentTimeline.t)}`);
        if (!sliderChanging) {
            store.fetchByTime(currentTimeline);
        }
    }, [currentTimeline, sliderChanging]);

    // 当实验是Completed状态时，禁用Live模式
    useEffect(() => {
        if (store.experiment?.status === 2) {
            setIsLiveMode(false);
        }
    }, [store.experiment?.status]);

    const modeOptions = [
        { value: 'Replay', label: 'Replay' },
    ];
    if (store.experiment?.status === 1) {
        modeOptions.push({ value: 'Live', label: 'Live' });
    }

    return (<Flex align='center' justify='center' gap="small">
        <Flex className='status'>
            <Tooltip title={
                <span>{store.experiment?.name}:&nbsp;
                    {experimentStatusMap[store.experiment?.status]}</span>}
            >
                <Space style={{ paddingLeft: "4px" }}>
                    <FlickeringDot
                        width="10px"
                        height="10px"
                        borderRadius="50%"
                        intervalMs={store.experiment?.status === 1 ? 1000 : undefined}
                        backgroundColor={store.experiment?.status === 0 ? "gray" : store.experiment?.status === 1 ? "green" : store.experiment?.status === 2 ? "green" : "red"}
                    />
                    <Button
                        shape='circle'
                        type="text"
                        icon={<ReloadOutlined />}
                        onClick={() => store.init(store.expID)}
                    />
                </Space>
            </Tooltip>
        </Flex>
        <Flex align='center' className='player'>
            <Button shape="circle" size='small' type='text' onClick={prevIndex} disabled={currentIndex === 0}>
                <FastBackwardOutlined />
            </Button>
            <Button shape="circle" type='text' onClick={() => setIsPlaying(!isPlaying)}>
                {isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            </Button>
            <Button shape="circle" size='small' type='text' onClick={nextIndex} disabled={currentIndex === store.timeline.length - 1}>
                <FastForwardOutlined />
            </Button>
        </Flex>
        <Flex>
            <Slider
                min={0}
                max={store.timeline.length - 1}
                value={currentIndex}
                onChange={handleSliderChange}
                onChangeComplete={handleSliderChangeEnd}
                style={{ width: 'calc(52vw - 500px)' }}
                tooltip={{ formatter }}
            />
        </Flex>
        <Flex>
            <Flex vertical>
                <strong>Day {currentTimeline.day}</strong>
                {parseT(currentTimeline.t)}
            </Flex>
        </Flex>
        <Flex className="circle-wrap">
            <Select
                value={playInterval}
                onChange={value => setPlayInterval(value)}
                placement="topLeft"
                suffixIcon={<UpOutlined />}
                style={{ width: '90px' }}
                options={[
                    { value: 10000, label: '10s/step' },
                    { value: 5000, label: '5s/step' },
                    { value: 2000, label: '2s/step' },
                    { value: 1000, label: '1s/step' },
                    { value: 500, label: '0.5s/step' },
                    { value: 250, label: '0.25s/step' },
                    { value: 100, label: '0.1s/step' },
                ]}
            />
        </Flex>
        <Flex className="circle-wrap">
            <Select
                value={isLiveMode ? "Live" : "Replay"}
                onChange={value => setIsLiveMode(value === "Live")}
                placement="topLeft"
                suffixIcon={<UpOutlined />}
                style={{ width: '85px' }}
                options={modeOptions}
            />
        </Flex>
        {/* <Flex>
            <Tooltip title="Toolset (TODO)">
                <Button shape="circle" type="text" icon={<ToolOutlined />} />
            </Tooltip>
        </Flex> */}
    </Flex >);
});

export default TimelinePlayer;