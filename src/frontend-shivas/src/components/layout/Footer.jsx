"use client";
import { usePathname } from "next/navigation";
import React, { useState, useEffect } from "react";
import styles from "./Footer.module.css";

export default function Footer() {
  const pathname = usePathname();
  const hideFooter = pathname === "/chat";
  const [userData, setUserData] = useState({ language_level: "NA", xp: 0 });

  useEffect(() => {
    // Simulate fetching user data
    const mockUserData = {
      language_level: "Intermediate",
      xp: 45,
    };

    // Simulate a delay like a fetch call
    const fetchUserData = () => {
      setTimeout(() => {
        setUserData(mockUserData);
      }, 500);
    };

    fetchUserData();
  }, []);

  if (hideFooter) {
    return null;
  }

  const { language_level, xp } = userData;

  return (
    <footer className={styles.footer}>
      <div className={styles.level}>
        Level: <span className={styles.levelValue}>{language_level}</span>
      </div>
      <div className={styles.xpBarContainer}>
        <span className={styles.xpLabel}>XP:</span>
        <div className={styles.xpBar}>
          <div
            className={styles.xpProgress}
            style={{ width: `${Math.min(xp, 100)}%` }}
          ></div>
        </div>
        <span className={styles.xpValue}>{xp}</span>
        <span className={styles.xpMax}>/100</span>
      </div>
    </footer>
  );
}
