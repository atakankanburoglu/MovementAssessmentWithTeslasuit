using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using TsAPI.Types;
using TsSDK;


[Serializable]
public class ImuDataObject
{
    public TrainingType trainingType;
    public Dictionary<TsHumanBoneIndex, TsImuSensorData> imuData;
    public double timestamp;

    public ImuDataObject(TrainingType trainingType, Dictionary<TsHumanBoneIndex, TsImuSensorData> imuData, double timestamp)
    {
        this.trainingType = trainingType;
        this.imuData = imuData;
        this.timestamp = timestamp;
    }

    /**
     * filtered: Whether CSV should be filtered for transmission to Python
     */
    public String ToCSV(string seperator)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(timestamp.ToString(CultureInfo.InvariantCulture)).Append(seperator);
        sb.Append(this.trainingType).Append(seperator);

        foreach (var boneIndex in TsHumanBones.SuitBones)
        {

            if (imuData.TryGetValue(boneIndex, out var tsImuSensorData))
            {
                sb.Append(QuatToString(tsImuSensorData.quat9x, seperator));
                sb.Append(QuatToString(tsImuSensorData.quat6x, seperator));
                sb.Append(Vector3sToString(tsImuSensorData.gyro, seperator));
                sb.Append(Vector3sToString(tsImuSensorData.magn, seperator));
                sb.Append(Vector3sToString(tsImuSensorData.accel, seperator));
                sb.Append(Vector3sToString(tsImuSensorData.linear_accel, seperator));
            }

        }

        return sb.ToString();
    }

    private string QuatToString(TsQuat quat, string seperator)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(quat.w.ToString(CultureInfo.InvariantCulture)).Append(seperator)
            .Append(quat.x.ToString(CultureInfo.InvariantCulture)).Append(seperator)
            .Append(quat.y.ToString(CultureInfo.InvariantCulture)).Append(seperator)
            .Append(quat.z.ToString(CultureInfo.InvariantCulture)).Append(seperator);

        return sb.ToString();
    }

    private string Vector3sToString(TsVec3f vec, string separator)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(vec.x.ToString(CultureInfo.InvariantCulture)).Append(separator)
            .Append(vec.y.ToString(CultureInfo.InvariantCulture)).Append(separator)
            .Append(vec.z.ToString(CultureInfo.InvariantCulture)).Append(separator);

        return sb.ToString();
    }

    public String GetCsvHeader(string seperator)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append("Timestamp").Append(seperator);
        sb.Append("TrainingType").Append(seperator);

        foreach (var boneIndex in TsHumanBones.SuitBones)
        {
            String nodeName = Enum.GetName(typeof(TsHumanBoneIndex), boneIndex);

            foreach (var property in Config.propertyNames)
            {
                // For Quats, add w component
                if (property.Equals("quat9x") || property.Equals("quat6x"))
                {
                    sb.Append(nodeName + "_" + property + "_w").Append(seperator);
                }

                // Everything else has x, y, z.
                sb.Append(nodeName + "_" + property + "_x").Append(seperator);
                sb.Append(nodeName + "_" + property + "_y").Append(seperator);
                sb.Append(nodeName + "_" + property + "_z").Append(seperator);
            }
        }

        sb.Append("\n");
        return sb.ToString();
    }

}
