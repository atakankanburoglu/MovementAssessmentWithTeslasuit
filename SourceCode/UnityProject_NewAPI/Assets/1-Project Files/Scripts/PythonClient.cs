using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Threading;
using UnityEngine;
using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using Debug = UnityEngine.Debug;
using System.IO;
using Newtonsoft.Json;


public class PythonClient
{
    private Thread _senderThread;
    private Thread _receiverThread;
    private Queue imuDataQueue = new Queue();
    private Boolean sendHeader = false;
    private Boolean running = false;

    //for Finishing Training Data Transfer
    private State trainingMode = State.IDLE;
    private string sampleInfo;
    private SampleType sampleType;

    //for Model Creation
    private Boolean createModel = false;
    private string modelInfo;

    //for Feedback
    private State testingMode = State.IDLE;
    private bool getModels = false;
    private string modelInfoForTesting;

    //private MotionFeedback _motionFeedback;
    //private MocapJoints _mocapJoints;
    private DataGateway _dataGateway;

    public PythonClient()
    {
        //_mocapJoints = MocapJoints.GetInstance();
        //_motionFeedback = GameObject.Find("Teslasuit_Man").GetComponent<MotionFeedback>();
        _dataGateway = GameObject.Find("DataGateway").GetComponent<DataGateway>();
        _senderThread = new Thread(RunSend);
        _senderThread.Start();
        _receiverThread = new Thread(RunReceive);
        _receiverThread.Start();
        running = true;
    }

    private void RunSend()
    {
        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use, not sure why yet
        using (PublisherSocket publisher = new PublisherSocket())
        {
            publisher.Bind("tcp://*:5555");
            while (running)
            {
                if (imuDataQueue.Count > 0 && (trainingMode == State.RUNNING || testingMode == State.RUNNING))
                {
                    
                    ImuDataObject dataToSend = (ImuDataObject)imuDataQueue.Dequeue();
                    if (sendHeader)
                    {
                        string header = dataToSend.GetCsvHeader(";");
                        publisher.SendFrame("ImuDataStream " + header);
                        string csv = dataToSend.ToCSV(";");
                        publisher.SendFrame("ImuDataStream " + csv);
                        sendHeader = false;
                    }
                    else
                    {
                        string csv = dataToSend.ToCSV(";");
                        publisher.SendFrame("ImuDataStream " + csv);
                    }

                }
                if(trainingMode == State.FINISHED)
                {
                    publisher.SendFrame("TrainingMode " + trainingMode + ";" + sampleType);
                    trainingMode = State.IDLE;
                }
                if (trainingMode == State.INIT)
                {
                    publisher.SendFrame("TrainingMode " + trainingMode + ";" + sampleInfo);
                    trainingMode = State.RUNNING;
                    sendHeader = true;
                }
                if (createModel)
                {
                    publisher.SendFrame("CreateModel " + modelInfo);
                    createModel = false;
                }
                if (testingMode == State.INIT)
                {
                    if (getModels)
                    {
                        publisher.SendFrame("TestingMode " + testingMode);

                    } else
                    {
                        publisher.SendFrame("TestingMode " + testingMode + ";" + modelInfoForTesting);
                        testingMode = State.RUNNING;
                    }
                
                }
                if (testingMode == State.FINISHED)
                {
                    publisher.SendFrame("TestingMode " + testingMode);
                    testingMode = State.IDLE;
                }
                Thread.Sleep(1);
            }
        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet
    }

    private void RunReceive()
    {
        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use, not sure why yet
        using (SubscriberSocket subscriber = new SubscriberSocket())
        {
            subscriber.Connect("tcp://localhost:6666");
            //subscriber.Subscribe("ErrorResponseStream");
            subscriber.SubscribeToAnyTopic();

            while (running)
            {
                string payload = subscriber.ReceiveFrameString();
                String[] values = payload.Split(' ');
                String topic = values[0];
                string message = values[1];

                if(topic == "ErrorResponseStream")
                {

                    _dataGateway.OnExcerciseRecognized(message);
                } else
                if (topic == "TestingMode")
                {
                    _dataGateway.OnModelListReceived(message);
                }
                //PerformanceAnalyzer.GetInstance().DataPointReceived((int)float.Parse(values[1], CultureInfo.InvariantCulture));

                //TrainingType recognizedExercise = (TrainingType)Enum.Parse(typeof(TrainingType), values[0], true);
                //if (recognizedExercise != null)
                //{
                //    _dataGateway.recognizedExercise = recognizedExercise;
                //    Debug.Log($"Recognized: {recognizedExercise}");
                //}


                //int indexOffset = 2;
                //Dictionary<String, Vector3> motionErrors = new Dictionary<string, Vector3>();

                //for (var i = 0; i < _mocapJoints.JointNames.Count; i++)
                //{
                //    Vector3 error = new Vector3(
                //        float.Parse(values[indexOffset + i * 3], CultureInfo.InvariantCulture),
                //        float.Parse(values[indexOffset + i * 3 + 1], CultureInfo.InvariantCulture),
                //        float.Parse(values[indexOffset + i * 3 + 2], CultureInfo.InvariantCulture));

                //    if (!error.Equals(Vector3.zero))
                //    {
                //        motionErrors[_mocapJoints.JointNames[i]] = error;
                //    }
                //}

                //_motionFeedback.MotionError = motionErrors;
                //PerformanceAnalyzer.GetInstance().ErrorReceived((int)float.Parse(values[1], CultureInfo.InvariantCulture));
                Thread.Sleep(1);
            }
        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet
    }

    public void PushSuitData(ImuDataObject data)
    {
        imuDataQueue.Enqueue(data);
    }

    public void StartTrainingMode(String subjectId, TrainingType trainingType)
    {
        trainingMode = State.INIT;
        this.sampleInfo = subjectId + "_" + trainingType;
    }

    public void StopTrainingMode(SampleType sampleType)
    {
        trainingMode = State.FINISHED;
        this.sampleType = sampleType;
    }

    public void CreateNewModel(String subjectIds, TrainingType trainingType, Algorithm algorithm)
    {
        createModel = true;
        modelInfo = subjectIds + "_" + trainingType + "_" + algorithm;
    }

    public void GetModels()
    {
        testingMode = State.INIT;
        getModels = true;
    }

    public void StartTestingMode(String algorithm, Boolean newRecognitionModel)
    {
        testingMode = State.INIT;
        modelInfoForTesting = algorithm + "_" + newRecognitionModel;
    }

    public void StopTestingMode()
    {
        testingMode = State.FINISHED;
    }

    public void Stop()
    {
        running = false;
        // block main thread, wait for _runnerThread to finish its job first, so we can be sure that 
        // _runnerThread will end before main thread end
        _senderThread.Join();
        _receiverThread.Join();
    }
}