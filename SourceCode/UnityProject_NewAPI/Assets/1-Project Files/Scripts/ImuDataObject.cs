using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using TsAPI.Types;
using TsSDK;


[Serializable]
public class ImuDataObject
{
    public TrainingType type;
    public Dictionary<TsHumanBoneIndex, TsImuSensorData> imuData;
    public double timestamp;

    public ImuDataObject(TrainingType type, Dictionary<TsHumanBoneIndex, TsImuSensorData> imuData, double timestamp)
    {
        this.type = type;
        this.imuData = imuData;
        this.timestamp = timestamp;
    }

    /**
     * filtered: Whether CSV should be filtered for transmission to Python
     */
    public String ToCSV(string seperator, bool filtered = false)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(timestamp.ToString(CultureInfo.InvariantCulture)).Append(seperator);
        if (!filtered) sb.Append(type.ToString()).Append(seperator);

        foreach (var boneIndex in TsHumanBones.SuitBones)
        {
            TsImuSensorData tsImuSensorData;
            if (imuData.TryGetValue(boneIndex, out tsImuSensorData))
            {

                if (!filtered)
                {
                    sb.Append(boneIndex.ToString()).Append(seperator);
                }

                if (Config.StreamedProperties["quat9x"] && (!filtered || Config.FilteredProperties["quat9x"]))
                    sb.Append(quatToString(tsImuSensorData.quat9x, seperator));
                if (Config.StreamedProperties["quat6x"] && (!filtered || Config.FilteredProperties["quat6x"]))
                    sb.Append(quatToString(tsImuSensorData.quat6x, seperator));
                if (Config.StreamedProperties["gyroscope"] && (!filtered || Config.FilteredProperties["gyroscope"]))
                    sb.Append(vector3sToString(tsImuSensorData.gyro, seperator));
                if (Config.StreamedProperties["magnetometer"] && (!filtered || Config.FilteredProperties["magnetometer"]))
                    sb.Append(vector3sToString(tsImuSensorData.magn, seperator));
                if (Config.StreamedProperties["accelerometer"] && (!filtered || Config.FilteredProperties["accelerometer"]))
                    sb.Append(vector3sToString(tsImuSensorData.accel, seperator));
                if (Config.StreamedProperties["linearAccel"] && (!filtered || Config.FilteredProperties["linearAccel"]))
                    sb.Append(vector3sToString(tsImuSensorData.linear_accel, seperator, endLine: boneIndex == TsHumanBoneIndex.RightLittleDistal));
            }

        }

        return sb.ToString();
    }

    private string quatToString(TsQuat quat, string seperator)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(quat.w.ToString(CultureInfo.InvariantCulture)).Append(seperator)
            .Append(quat.x.ToString(CultureInfo.InvariantCulture)).Append(seperator)
            .Append(quat.y.ToString(CultureInfo.InvariantCulture)).Append(seperator)
            .Append(quat.z.ToString(CultureInfo.InvariantCulture)).Append(seperator);

        return sb.ToString();
    }

    private string vector3sToString(TsVec3f vec, string separator, bool endLine = false)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(vec.x.ToString(CultureInfo.InvariantCulture)).Append(separator)
            .Append(vec.y.ToString(CultureInfo.InvariantCulture)).Append(separator)
            .Append(vec.z.ToString(CultureInfo.InvariantCulture)).Append(separator);

        if (!endLine)
        {
            sb.Append(separator);
        }

        return sb.ToString();
    }

    public String GetCsvHeader(string seperator)
    {
        StringBuilder sb = new StringBuilder();
        sb.Append("TsHumanBoneIndex").Append(seperator).Append("TrainingType").Append(seperator).Append("Segment").Append(seperator);

        foreach (var boneIndex in TsHumanBones.SuitBones)
        {
            TsImuSensorData tsImuSensorData;
            if (imuData.TryGetValue(boneIndex, out tsImuSensorData))
            {

                String nodeName = Enum.GetName(typeof(TsHumanBoneIndex), boneIndex);
                sb.Append(nodeName + "_boneIndex").Append(seperator);

                foreach (var property in Config.propertyNames)
                {
                    // Property not streamed -> Continue
                    if (!Config.StreamedProperties[property])
                        continue;

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
        }

        sb.Append("\n");
        return sb.ToString();
    }

}
