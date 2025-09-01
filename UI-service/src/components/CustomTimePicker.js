import React, { useState, useEffect } from 'react';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

const CustomTimePicker = ({ value, onChange, required, disabled }) => {
  const [selectedTime, setSelectedTime] = useState(null);

  // Convert HH:MM string to Date object
  const timeStringToDate = (timeString) => {
    if (!timeString) return null;
    try {
      const [hours, minutes] = timeString.split(':').map(Number);
      const date = new Date();
      date.setHours(hours, minutes, 0, 0);
      return date;
    } catch {
      return null;
    }
  };

  // Convert Date object to HH:MM string
  const dateToTimeString = (date) => {
    if (!date) return '';
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  useEffect(() => {
    setSelectedTime(timeStringToDate(value));
  }, [value]);

  const handleTimeChange = (date) => {
    setSelectedTime(date);
    const timeString = dateToTimeString(date);
    onChange({ target: { name: 'planTime', value: timeString } });
  };

  return (
    <div className="custom-time-picker">
      <DatePicker
        selected={selectedTime}
        onChange={handleTimeChange}
        showTimeSelect
        showTimeSelectOnly
        timeIntervals={15}
        timeCaption="Time"
        dateFormat="h:mm aa"
        placeholderText="Select time"
        required={required}
        disabled={disabled}
        className="form-input"
        timeFormat="HH:mm"
        minTime={new Date().setHours(0, 0, 0, 0)}
        maxTime={new Date().setHours(23, 45, 0, 0)}
      />
    </div>
  );
};

export default CustomTimePicker;
